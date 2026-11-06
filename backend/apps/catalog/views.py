import secrets

from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from django.utils.crypto import salted_hmac
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.core.audit import record
from apps.core.models import SiteSettings

from .concurrency import VersionErrorSerializer, check_version, version_parameter
from .models import Category, Publication, Rating
from .permissions import PublicArchiveAvailable, can_edit, can_publish
from .revisions import capture, resolve_document
from .serializers import CategorySerializer, PublicationSerializer, RevisionSerializer
from .throttles import RatingThrottle


def publication_query():
    return (
        Publication.objects.select_related("document", "owner")
        .prefetch_related("category_links__category", "credits__person")
        .annotate(
            rating_average=Avg("ratings__score", default=0),
            rating_count=Count("ratings", distinct=True),
        )
    )


class PublicPublicationViewSet(ReadOnlyModelViewSet):
    serializer_class = PublicationSerializer
    permission_classes = [PublicArchiveAvailable]
    authentication_classes = []
    lookup_field = "slug"

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "site": SiteSettings.current()}

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Publication.objects.none()
        qs = publication_query().filter(status="published", document__state="ready")
        if self.action != "list":
            return qs
        if year := self.request.query_params.get("year"):
            if not year.isdigit() or len(year) > 4 or not 1 <= int(year) <= 9999:
                return qs.none()
            qs = qs.filter(publication_date__year=int(year))
        if category := self.request.query_params.get("category"):
            qs = qs.filter(categories__slug=category)
        if q := self.request.query_params.get("q", "").strip():
            # PostgreSQL unaccent é configurado pela migração; a busca ocorre no banco.
            qs = qs.filter(
                Q(title__unaccent__icontains=q)
                | Q(description__unaccent__icontains=q)
                | Q(categories__name__unaccent__icontains=q)
            )
        return qs.distinct().order_by("-publication_date", "-created_at", "-pk")

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        document, snapshot = resolve_document(obj, request.query_params.get("document"))
        obj.document = document
        result = self.get_serializer(obj).data
        if snapshot:
            result.update(snapshot)
        return Response(result)


@extend_schema_view(
    partial_update=extend_schema(
        parameters=[version_parameter],
        responses={
            200: PublicationSerializer,
            412: VersionErrorSerializer,
            428: VersionErrorSerializer,
        },
    ),
)
class AdminPublicationViewSet(ModelViewSet):
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Publication.objects.none()
        qs = publication_query()
        if not can_publish(self.request.user):
            qs = qs.filter(owner=self.request.user)
        if self.action != "list":
            return qs
        if status := self.request.query_params.get("status"):
            qs = qs.filter(status=status)
        if q := self.request.query_params.get("q"):
            qs = qs.filter(title__icontains=q)
        return qs.order_by("-publication_date", "-created_at", "-pk")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key = serializer.validated_data.get("client_key")

        def existing():
            obj = Publication.objects.filter(client_key=key).first() if key else None
            if obj is not None:
                if obj.owner_id != request.user.pk:
                    raise PermissionDenied()
                return Response(self.get_serializer(obj).data, status=200)
            return None

        if response := existing():
            return response
        try:
            with transaction.atomic():
                obj = serializer.save()
                record(request, "publication.create", obj, serializer.validated_data)
                capture(request, obj)
        except IntegrityError:
            if response := existing():
                return response
            raise
        return Response(serializer.data, status=201)

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "private": True, "site": SiteSettings.current()}

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        document, snapshot = resolve_document(
            obj, request.query_params.get("document"), private=True
        )
        obj.document = document
        result = self.get_serializer(obj).data
        if snapshot:
            result.update(snapshot)
        return Response(result)

    @extend_schema(responses=RevisionSerializer(many=True))
    @action(detail=True, methods=["get"])
    def revisions(self, request, pk=None):
        obj = self.get_object()
        query = obj.revisions.select_related("document", "publication").all()
        page = self.paginate_queryset(query)
        serializer = RevisionSerializer(page if page is not None else query, many=True)
        return (
            self.get_paginated_response(serializer.data)
            if page is not None
            else Response(serializer.data)
        )

    @transaction.atomic
    def perform_update(self, serializer):
        obj = Publication.objects.select_for_update().get(pk=serializer.instance.pk)
        if not can_edit(self.request.user, obj):
            raise PermissionDenied()
        check_version(self.request, obj)
        obj.edit_version += 1
        if not obj.revisions.exists():
            capture(self.request, obj)
        serializer.instance = obj
        updated = serializer.save()
        record(self.request, "publication.update", updated, serializer.validated_data)
        capture(self.request, updated)
        serializer.instance = self.get_queryset().get(pk=updated.pk)

    @extend_schema(
        request=None,
        responses={
            200: PublicationSerializer,
            412: VersionErrorSerializer,
            428: VersionErrorSerializer,
        },
        parameters=[version_parameter],
    )
    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        if not can_publish(request.user):
            raise PermissionDenied()
        with transaction.atomic():
            obj = self.get_object()
            obj = (
                Publication.objects.select_for_update(of=("self",))
                .select_related("document")
                .get(pk=obj.pk)
            )
            check_version(request, obj)
            if (
                not obj.document_id
                or obj.document.state != "ready"
                or not obj.categories.exists()
                or not obj.title.strip()
            ):
                return Response(
                    {
                        "detail": "Envie um PDF processado e complete as informações antes de publicar."
                    },
                    status=409,
                )
            if not obj.revisions.exists():
                capture(request, obj)
            obj.edit_version += 1
            obj.status = "published"
            obj.save()
            record(request, "publication.publish", obj, ["status"])
            capture(request, obj)
        return Response(self.get_serializer(self.get_object()).data)

    @extend_schema(
        request=None,
        responses={
            200: PublicationSerializer,
            412: VersionErrorSerializer,
            428: VersionErrorSerializer,
        },
        parameters=[version_parameter],
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def archive(self, request, pk=None):
        if not can_publish(request.user):
            raise PermissionDenied()
        visible = self.get_object()
        obj = Publication.objects.select_for_update().get(pk=visible.pk)
        check_version(request, obj)
        if not obj.revisions.exists():
            capture(request, obj)
        obj.edit_version += 1
        obj.status = "archived"
        obj.save()
        record(request, "publication.archive", obj, ["status"])
        capture(request, obj)
        return Response(self.get_serializer(obj).data)

    @extend_schema(
        request=None,
        responses={
            200: PublicationSerializer,
            412: VersionErrorSerializer,
            428: VersionErrorSerializer,
        },
        parameters=[version_parameter],
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def restore(self, request, pk=None):
        if not can_publish(request.user):
            raise PermissionDenied()
        visible = self.get_object()
        obj = Publication.objects.select_for_update().get(pk=visible.pk)
        check_version(request, obj)
        if not obj.revisions.exists():
            capture(request, obj)
        obj.edit_version += 1
        obj.status = "draft"
        obj.save()
        record(request, "publication.restore", obj, ["status"])
        capture(request, obj)
        return Response(self.get_serializer(obj).data)


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "head", "options"]
    queryset = Category.objects.annotate(
        count=Count(
            "publications",
            filter=Q(publications__status="published", publications__document__state="ready"),
            distinct=True,
        )
    ).order_by("position", "name", "pk")

    @transaction.atomic
    def perform_create(self, serializer):
        if not can_publish(self.request.user):
            raise PermissionDenied()
        obj = serializer.save()
        record(self.request, "category.create", obj, serializer.validated_data)

    @transaction.atomic
    def perform_update(self, serializer):
        if not can_publish(self.request.user):
            raise PermissionDenied()
        obj = serializer.save()
        record(self.request, "category.update", obj, serializer.validated_data)


class PublicCategoryViewSet(ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [PublicArchiveAvailable]
    authentication_classes = []
    lookup_field = "slug"
    queryset = (
        Category.objects.filter(active=True)
        .annotate(
            count=Count(
                "publications",
                filter=Q(publications__status="published", publications__document__state="ready"),
                distinct=True,
            )
        )
        .order_by("position", "name", "pk")
    )


class ScoreSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=1, max_value=5)


class CurrentScoreSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=1, max_value=5, allow_null=True)


@method_decorator(csrf_protect, name="dispatch")
class RatingView(APIView):
    permission_classes = [PublicArchiveAvailable]
    throttle_classes = [RatingThrottle]

    def publication(self, slug):
        if not SiteSettings.current().ratings_enabled:
            raise PermissionDenied("As avaliações estão desativadas.")
        return get_object_or_404(
            Publication, slug=slug, status="published", document__state="ready"
        )

    def identity(self, request):
        raw = request.get_signed_cookie("revista_visitor", default="", salt="rating")
        return raw or secrets.token_urlsafe(24)

    @extend_schema(responses=CurrentScoreSerializer, tags=["ratings"])
    def get(self, request, slug):
        pub = self.publication(slug)
        raw = self.identity(request)
        identity = salted_hmac("visitor", raw).hexdigest()
        rating = Rating.objects.filter(publication=pub, visitor=identity).first()
        response = Response({"score": rating.score if rating else None})
        response.set_signed_cookie(
            "revista_visitor",
            raw,
            salt="rating",
            httponly=True,
            samesite="Lax",
            secure=request.is_secure(),
            max_age=31536000,
        )
        return response

    @extend_schema(request=ScoreSerializer, responses=ScoreSerializer, tags=["ratings"])
    def post(self, request, slug):
        pub = self.publication(slug)
        serializer = ScoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw = self.identity(request)
        identity = salted_hmac("visitor", raw).hexdigest()
        Rating.objects.update_or_create(
            publication=pub,
            visitor=identity,
            defaults={"score": serializer.validated_data["score"]},
        )
        response = Response({"score": serializer.validated_data["score"]})
        response.set_signed_cookie(
            "revista_visitor",
            raw,
            salt="rating",
            httponly=True,
            samesite="Lax",
            secure=request.is_secure(),
            max_age=31536000,
        )
        return response


class CatalogSummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    years = serializers.ListField(child=serializers.IntegerField())
    featured = PublicationSerializer(allow_null=True)


class CatalogSummaryView(APIView):
    permission_classes = [PublicArchiveAvailable]
    authentication_classes = []

    @extend_schema(responses=CatalogSummarySerializer, tags=["catalog"])
    def get(self, request):
        qs = publication_query().filter(status="published", document__state="ready")
        featured = qs.order_by("-publication_date", "-created_at", "-pk").first()
        return Response(
            {
                "total": qs.count(),
                "years": [date.year for date in qs.dates("publication_date", "year", order="DESC")],
                "featured": PublicationSerializer(
                    featured, context={"site": SiteSettings.current()}
                ).data
                if featured
                else None,
            }
        )
