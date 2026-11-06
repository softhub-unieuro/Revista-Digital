import re
from contextlib import closing
from pathlib import Path

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import content_disposition_header
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import APIException
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Publication
from apps.catalog.permissions import PublicArchiveAvailable, can_publish
from apps.catalog.revisions import resolve_document
from apps.catalog.serializers import DocumentSerializer
from apps.core.audit import record
from apps.core.models import SiteSettings

from .models import Document
from .tasks import process_document


class PdfTooLarge(APIException):
    status_code = 413
    default_code = "pdf_size_limit"


class UploadSizeErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if value.size > settings.MAX_PDF_BYTES:
            raise PdfTooLarge(
                f"O tamanho máximo permitido é {settings.MAX_PDF_BYTES / (1024 * 1024):g} MiB."
            )
        header = value.read(5)
        value.seek(0)
        if header != b"%PDF-":
            raise serializers.ValidationError("Envie um arquivo PDF válido.")
        return value


def owned_documents(user):
    return Document.objects.all() if can_publish(user) else Document.objects.filter(owner=user)


class UploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=UploadSerializer,
        responses={202: DocumentSerializer, 413: UploadSizeErrorSerializer},
        tags=["documents"],
    )
    def post(self, request):
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        name = Path(file.name).name.replace("\r", " ").replace("\n", " ")[:255]
        doc = Document.objects.create(
            owner=request.user, file=file, original_name=name, size_bytes=file.size
        )
        record(request, "document.upload", doc, ["file"])
        try:
            process_document.delay(str(doc.pk))
        except Exception:
            # O registro persistente permite tentar novamente após a volta da fila.
            return Response(
                {
                    **DocumentSerializer(doc).data,
                    "detail": "A fila está indisponível. Tente o processamento novamente.",
                },
                status=503,
            )
        return Response(DocumentSerializer(doc).data, status=status.HTTP_202_ACCEPTED)


class JobView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=DocumentSerializer, tags=["documents"])
    def get(self, request, pk):
        doc = get_object_or_404(owned_documents(request.user), pk=pk)
        return Response(DocumentSerializer(doc).data)


class RetryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={202: DocumentSerializer}, tags=["documents"])
    def post(self, request, pk):
        doc = get_object_or_404(owned_documents(request.user), pk=pk)
        if doc.state in {"processing", "ready"}:
            return Response(DocumentSerializer(doc).data, status=409)
        doc.state = "queued"
        doc.error_code = doc.error_message = ""
        doc.save()
        try:
            process_document.delay(str(doc.pk))
        except Exception:
            return Response({"detail": "A fila está indisponível. Tente novamente."}, status=503)
        return Response(DocumentSerializer(doc).data, status=202)


def stream_file(request, path, filename, content_type, etag, attachment=False):
    size = path.stat().st_size
    start, end = 0, size - 1
    partial = False
    range_header = request.headers.get("Range") if request.method == "GET" else None
    if range_header and request.headers.get("If-Range", etag) == etag:
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", range_header)
        try:
            if not match or not any(match.groups()):
                raise ValueError
            left, right = match.groups()
            if left:
                start = int(left)
                end = min(int(right), end) if right else end
            else:
                length = int(right)
                if length <= 0:
                    raise ValueError
                start = max(0, size - length)
            if start >= size or end < start:
                raise ValueError
            partial = True
        except ValueError:
            response = HttpResponse(status=416)
            response["Content-Range"] = f"bytes */{size}"
            response["Cache-Control"] = "no-store"
            return response

    if settings.USE_X_ACCEL_REDIRECT:
        from urllib.parse import quote

        try:
            relative = path.resolve().relative_to(settings.MEDIA_ROOT.resolve())
        except ValueError:
            return HttpResponse(status=404)
        response = HttpResponse(content_type=content_type)
        response["X-Accel-Redirect"] = "/_protected/" + quote(relative.as_posix(), safe="/")
        response["Content-Disposition"] = content_disposition_header(attachment, filename)
        response["Cache-Control"] = "no-store"
        response["X-Content-Type-Options"] = "nosniff"
        return response

    def chunks():
        with path.open("rb") as file:
            file.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = file.read(min(65536, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk

    response = (
        HttpResponse(content_type=content_type)
        if request.method == "HEAD"
        else StreamingHttpResponse(
            chunks(), content_type=content_type, status=206 if partial else 200
        )
    )
    response["Content-Length"] = str(end - start + 1)
    response["Accept-Ranges"] = "bytes"
    response["ETag"] = etag
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    response["Content-Disposition"] = content_disposition_header(attachment, filename)
    if partial:
        response["Content-Range"] = f"bytes {start}-{end}/{size}"
    return response


class DocumentFileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={(200, "application/pdf"): bytes, (206, "application/pdf"): bytes},
        tags=["documents"],
    )
    def get(self, request, pk):
        user = request.user
        readable = (
            Document.objects.all()
            if can_publish(user)
            else Document.objects.filter(
                Q(owner=user)
                | Q(publication__owner=user)
                | Q(publication_revisions__publication__owner=user)
            ).distinct()
        )
        doc = get_object_or_404(readable, pk=pk, state="ready")
        cover = request.query_params.get("kind") == "cover"
        path = Path(settings.MEDIA_ROOT / doc.cover) if cover else Path(doc.file.path)
        if not path.is_file():
            return HttpResponse(status=404)
        return stream_file(
            request,
            path,
            "capa.jpg" if cover else doc.original_name,
            "image/jpeg" if cover else "application/pdf",
            f'"{doc.sha256}-{Path(doc.cover).stem if cover else "pdf"}"',
            request.query_params.get("download") == "1",
        )

    head = get


class PublicFileView(APIView):
    permission_classes = [PublicArchiveAvailable]
    authentication_classes = []

    @extend_schema(
        operation_id="public_publication_file",
        responses={(200, "application/pdf"): bytes, (206, "application/pdf"): bytes},
        tags=["documents"],
    )
    def get(self, request, slug, kind):
        if kind == "download" and not SiteSettings.current().downloads_enabled:
            return Response({"detail": "Os downloads estão desativados."}, status=403)
        if kind not in {"file", "download", "cover"}:
            return HttpResponse(status=404)
        pub = get_object_or_404(
            Publication.objects.select_related("document"),
            slug=slug,
            status="published",
            document__state="ready",
        )
        doc, _snapshot = resolve_document(pub, request.query_params.get("v"))
        cover = kind == "cover"
        path = Path(settings.MEDIA_ROOT / doc.cover) if cover else Path(doc.file.path)
        if not path.is_file():
            return HttpResponse(status=404)
        return stream_file(
            request,
            path,
            "capa.jpg" if cover else doc.original_name,
            "image/jpeg" if cover else "application/pdf",
            f'"{doc.sha256}-{Path(doc.cover).stem if cover else "pdf"}"',
            kind == "download",
        )

    head = get


class CoverUploadSerializer(serializers.Serializer):
    file = serializers.ImageField(required=False)
    reset = serializers.BooleanField(required=False, default=False)


class CoverView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @extend_schema(request=CoverUploadSerializer, responses=DocumentSerializer, tags=["documents"])
    def post(self, request, pk):
        import uuid
        from io import BytesIO

        import pypdfium2 as pdfium
        from PIL import Image, ImageOps

        doc = get_object_or_404(owned_documents(request.user), pk=pk, state="ready")
        if not can_publish(request.user) and (
            doc.publication_set.exclude(status="draft").exists()
            or doc.publication_revisions.filter(status="published").exists()
        ):
            return Response({"detail": "Somente editores podem alterar esta capa."}, status=403)
        serializer = CoverUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data.get("file")
        reset = serializer.validated_data["reset"]
        if not file and not reset:
            return Response({"detail": "Selecione uma imagem ou a primeira página."}, status=400)
        if file and file.size > 5 * 1024 * 1024:
            return Response({"detail": "A imagem deve ter até 5 MiB."}, status=400)
        image = None
        try:
            if reset:
                with pdfium.PdfDocument(doc.file.path) as pdf:
                    with closing(pdf[0]) as page:
                        width, height = page.get_size()
                        with closing(
                            page.render(scale=min(1000 / width, 1400 / height, 2))
                        ) as bitmap:
                            image = bitmap.to_pil().copy()
            else:
                # ImageField verifica formato; limitar pixels antes de decodificar.
                image = Image.open(BytesIO(file.read()))
                if image.format not in {"JPEG", "PNG"} or image.width * image.height > 16000000:
                    return Response({"detail": "Use JPG ou PNG de até 16 megapixels."}, status=400)
                image.load()
            oriented = ImageOps.exif_transpose(image)
            image.close()
            image = oriented
            image.thumbnail((1000, 1400))
            name = f"covers/{doc.pk}-{uuid.uuid4()}.jpg"
            path = settings.MEDIA_ROOT / name
            path.parent.mkdir(parents=True, exist_ok=True)
            image.convert("RGB").save(path, format="JPEG", quality=85)
            doc.cover = name
            doc.save(update_fields=["cover", "updated_at"])
            record(request, "document.cover", doc, ["cover"])
        finally:
            if image is not None:
                image.close()
        return Response(DocumentSerializer(doc).data)
