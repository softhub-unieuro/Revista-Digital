import hashlib
import logging
import math
import uuid
from datetime import timedelta

import pypdfium2 as pdfium
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from pypdf import PdfReader

from .models import Document

logger = logging.getLogger(__name__)


class InvalidPdf(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


@shared_task(bind=True, acks_late=True, reject_on_worker_lost=True, max_retries=20)
def process_document(self, document_id):
    token = uuid.uuid4()
    with transaction.atomic():
        doc = Document.objects.select_for_update().filter(pk=document_id).first()
        if doc is None:
            return {"state": "expired"}
        if doc.state == Document.State.READY:
            return {"state": "ready"}
        if (
            doc.state == Document.State.PROCESSING
            and doc.started_at
            and doc.started_at > timezone.now() - timedelta(seconds=130)
        ):
            raise self.retry(countdown=10)
        doc.state = Document.State.PROCESSING
        doc.lease = token
        doc.started_at = timezone.now()
        doc.error_code = doc.error_message = ""
        doc.save()
    cover_path = None
    try:
        if doc.file.size > settings.MAX_PDF_BYTES:
            raise InvalidPdf("pdf_size_limit", "O PDF excede o tamanho máximo permitido.")
        with doc.file.open("rb") as file:
            reader = PdfReader(file, strict=True)
            if reader.is_encrypted:
                raise InvalidPdf("pdf_encrypted", "Envie um PDF sem proteção por senha.")
            count = len(reader.pages)
            if not 1 <= count <= 300:
                raise InvalidPdf(
                    "pdf_page_limit", f"O PDF possui {count} páginas. O máximo permitido é 300."
                )
        with doc.file.open("rb") as file:
            digest = hashlib.file_digest(file, "sha256").hexdigest()
        native = pdfium.PdfDocument(doc.file.path)
        try:
            page = native[0]
            try:
                width, height = page.get_size()
                if not all(math.isfinite(n) and 0 < n <= 14400 for n in (width, height)):
                    raise InvalidPdf(
                        "pdf_page_dimensions", "As dimensões da página não são suportadas."
                    )
                bitmap = page.render(scale=min(1000 / width, 1400 / height, 2))
                try:
                    image = bitmap.to_pil()
                    relative = f"covers/{doc.pk}-{token}.jpg"
                    cover_path = settings.MEDIA_ROOT / relative
                    cover_path.parent.mkdir(parents=True, exist_ok=True)
                    image.convert("RGB").save(cover_path, format="JPEG", quality=85)
                    image.close()
                finally:
                    bitmap.close()
            finally:
                page.close()
        finally:
            native.close()
        updated = Document.objects.filter(pk=doc.pk, lease=token).update(
            state=Document.State.READY,
            page_count=count,
            sha256=digest,
            size_bytes=doc.file.size,
            cover=relative,
            error_code="",
            error_message="",
            updated_at=timezone.now(),
        )
        if not updated and cover_path:
            cover_path.unlink(missing_ok=True)
        return {"state": "ready", "page_count": count}
    except Exception as error:
        if cover_path:
            cover_path.unlink(missing_ok=True)
        code = error.code if isinstance(error, InvalidPdf) else "invalid_pdf"
        message = (
            str(error)
            if isinstance(error, InvalidPdf)
            else "Não foi possível processar o PDF. Verifique o arquivo e tente novamente."
        )
        if not isinstance(error, InvalidPdf):
            logger.exception("Falha no processamento do documento %s", document_id)
        Document.objects.filter(pk=doc.pk, lease=token).update(
            state=Document.State.FAILED,
            error_code=code,
            error_message=message,
            updated_at=timezone.now(),
        )
        return {"state": "failed", "code": code}
