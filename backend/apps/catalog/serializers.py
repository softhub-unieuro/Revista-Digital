from django.db import transaction
from rest_framework import serializers

from apps.documents.models import Document

from .models import Category, Person, Publication, PublicationCategory, PublicationCredit
from .permissions import can_publish


class CategorySerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "icon", "active", "position", "count"]


class DocumentSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    cover_version = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "state",
            "page_count",
            "size_bytes",
            "original_name",
            "error_code",
            "error_message",
            "cover_url",
            "file_url",
            "cover_version",
        ]

    def get_cover_url(self, obj) -> str | None:
        return f"/api/v1/admin/files/{obj.pk}?kind=cover" if obj.cover else None

    def get_file_url(self, obj) -> str | None:
        return f"/api/v1/admin/files/{obj.pk}" if obj.state == "ready" else None


class PublicPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["id", "name", "institution", "biography"]


class PublicationSerializer(serializers.ModelSerializer):
    author_ids = serializers.PrimaryKeyRelatedField(
        queryset=Person.objects.filter(kind="author"), many=True, write_only=True, required=False
    )
    reviewer_ids = serializers.PrimaryKeyRelatedField(
        queryset=Person.objects.filter(kind="reviewer"), many=True, write_only=True, required=False
    )
    authors = serializers.SerializerMethodField()
    reviewers = serializers.SerializerMethodField()

    def get_authors(self, obj) -> list[dict]:
        return [
            PublicPersonSerializer(c.person).data for c in obj.credits.all() if c.kind == "author"
        ]

    def get_reviewers(self, obj) -> list[dict]:
        return [
            PublicPersonSerializer(c.person).data for c in obj.credits.all() if c.kind == "reviewer"
        ]

    client_key = serializers.UUIDField(required=False, write_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, write_only=True
    )
    categories = serializers.SerializerMethodField()
    document_id = serializers.PrimaryKeyRelatedField(
        source="document", queryset=Document.objects.filter(state="ready"), write_only=True
    )
    page_count = serializers.IntegerField(source="document.page_count", read_only=True, default=0)
    file_size_bytes = serializers.IntegerField(
        source="document.size_bytes", read_only=True, default=0
    )
    document_version = serializers.UUIDField(source="document_id", read_only=True)
    processing_state = serializers.CharField(source="document.state", read_only=True, default="")
    cover_url = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    rating_average = serializers.FloatField(read_only=True, default=0)
    rating_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Publication
        fields = [
            "id",
            "slug",
            "client_key",
            "title",
            "issue",
            "publication_date",
            "description",
            "status",
            "category_ids",
            "author_ids",
            "reviewer_ids",
            "authors",
            "reviewers",
            "categories",
            "document_id",
            "document_version",
            "page_count",
            "file_size_bytes",
            "processing_state",
            "cover_url",
            "file_url",
            "download_url",
            "rating_average",
            "rating_count",
            "updated_at",
            "edit_version",
        ]
        read_only_fields = ["id", "slug", "status", "updated_at", "edit_version"]

    def get_categories(self, obj) -> list[dict]:
        return [CategorySerializer(link.category).data for link in obj.category_links.all()]

    def get_cover_url(self, obj) -> str | None:
        if not obj.document_id or not obj.document.cover:
            return None
        if self.context.get("private"):
            return f"/api/v1/admin/files/{obj.document_id}?kind=cover"
        return f"/api/v1/public/publications/{obj.slug}/cover?v={obj.document_id}"

    def get_file_url(self, obj) -> str | None:
        if not obj.document_id:
            return None
        if self.context.get("private"):
            return f"/api/v1/admin/files/{obj.document_id}"
        return f"/api/v1/public/publications/{obj.slug}/file?v={obj.document_id}"

    def get_download_url(self, obj) -> str | None:
        if not self.context.get("private") and not self.context["site"].downloads_enabled:
            return None
        if self.context.get("private"):
            return self.get_file_url(obj) + "?download=1" if obj.document_id else None
        return f"/api/v1/public/publications/{obj.slug}/download?v={obj.document_id}"

    def validate_category_ids(self, value):
        if not value or len(set(x.pk for x in value)) != len(value):
            raise serializers.ValidationError("Selecione pelo menos uma categoria, sem repetições.")
        previous = (
            set(self.instance.category_links.values_list("category_id", flat=True))
            if self.instance
            else set()
        )
        if any(not category.active and category.pk not in previous for category in value):
            raise serializers.ValidationError("Selecione somente categorias ativas.")
        return value

    def validate_document_id(self, value):
        user = self.context["request"].user
        if value.owner_id != user.pk and not can_publish(user):
            raise serializers.ValidationError("O arquivo não está disponível para este usuário.")
        return value

    def validate(self, attrs):
        for key, kind in [("author_ids", "author"), ("reviewer_ids", "reviewer")]:
            if key in attrs:
                people = attrs[key]
                if len({p.pk for p in people}) != len(people):
                    raise serializers.ValidationError({key: "Não repita pessoas na mesma lista."})
                previous = (
                    set(self.instance.credits.filter(kind=kind).values_list("person_id", flat=True))
                    if self.instance
                    else set()
                )
                if any(not p.active and p.pk not in previous for p in people):
                    raise serializers.ValidationError({key: "Selecione somente pessoas ativas."})
        if (
            self.instance
            and "client_key" in attrs
            and attrs["client_key"] != self.instance.client_key
        ):
            raise serializers.ValidationError("A chave de criação não pode ser alterada.")
        if (
            self.instance
            and self.instance.status == "published"
            and not can_publish(self.context["request"].user)
        ):
            raise serializers.ValidationError(
                "Somente editores podem alterar uma publicação disponível ao público."
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        self._lock_document(validated_data)
        categories = validated_data.pop("category_ids")
        authors = validated_data.pop("author_ids", [])
        reviewers = validated_data.pop("reviewer_ids", [])
        obj = Publication.objects.create(owner=self.context["request"].user, **validated_data)
        self._categories(obj, categories)
        self._credits(obj, authors, "author")
        self._credits(obj, reviewers, "reviewer")
        return obj

    @transaction.atomic
    def update(self, instance, validated_data):
        self._lock_document(validated_data)
        categories = validated_data.pop("category_ids", None)
        authors = validated_data.pop("author_ids", None)
        reviewers = validated_data.pop("reviewer_ids", None)
        for name, value in validated_data.items():
            setattr(instance, name, value)
        instance.save()
        if categories is not None:
            self._categories(instance, categories)
        if authors is not None:
            self._credits(instance, authors, "author")
        if reviewers is not None:
            self._credits(instance, reviewers, "reviewer")
        return instance

    def _lock_document(self, values):
        if document := values.get("document"):
            if (
                not Document.objects.select_for_update()
                .filter(pk=document.pk, state="ready")
                .exists()
            ):
                raise serializers.ValidationError(
                    {"document_id": "O arquivo expirou ou não está pronto. Envie novamente."}
                )

    def _credits(self, obj, people, kind):
        obj.credits.filter(kind=kind).delete()
        PublicationCredit.objects.bulk_create(
            [
                PublicationCredit(publication=obj, person=p, kind=kind, position=i)
                for i, p in enumerate(people)
            ]
        )

    def _categories(self, obj, categories):
        obj.category_links.all().delete()
        PublicationCategory.objects.bulk_create(
            [
                PublicationCategory(publication=obj, category=c, position=i)
                for i, c in enumerate(categories)
            ]
        )


class RevisionSerializer(serializers.ModelSerializer):
    document_version = serializers.UUIDField(source="document_id", read_only=True)
    page_count = serializers.IntegerField(source="document.page_count", read_only=True)
    preview_url = serializers.SerializerMethodField()

    class Meta:
        from .models import PublicationRevision

        model = PublicationRevision
        fields = [
            "id",
            "document_version",
            "page_count",
            "status",
            "snapshot",
            "created_at",
            "preview_url",
        ]

    def get_preview_url(self, obj) -> str:
        return f"/ler/{obj.publication.slug}?preview={obj.publication_id}&version={obj.document_id}"
