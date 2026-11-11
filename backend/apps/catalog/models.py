import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=30, default="brain")
    active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "name"]


class Publication(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        PUBLISHED = "published", "Publicada"
        ARCHIVED = "archived", "Arquivada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_key = models.UUIDField(null=True, blank=True, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    title = models.CharField(max_length=255)
    issue = models.CharField(max_length=50)
    publication_date = models.DateField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    document = models.ForeignKey(
        "documents.Document", on_delete=models.PROTECT, null=True, blank=True
    )
    categories = models.ManyToManyField(
        Category, through="PublicationCategory", related_name="publications"
    )
    edit_version = models.PositiveBigIntegerField(default=1, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-publication_date", "-created_at"]
        indexes = [models.Index(fields=["status", "-publication_date"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = (slugify(self.title)[:65] or "edicao") + "-" + self.pk.hex[:8]
        super().save(*args, **kwargs)


class PublicationCategory(models.Model):
    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name="category_links"
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["publication", "category"], name="publication_category_unique"
            ),
            models.UniqueConstraint(
                fields=["publication", "position"], name="publication_category_order_unique"
            ),
        ]


class Rating(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="ratings")
    visitor = models.CharField(max_length=64)
    score = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["publication", "visitor"], name="one_rating_per_visitor"
            ),
            models.CheckConstraint(
                condition=models.Q(score__gte=1, score__lte=5), name="rating_score_range"
            ),
        ]


class Person(models.Model):
    class Kind(models.TextChoices):
        AUTHOR = "author", "Autor"
        REVIEWER = "reviewer", "Parecerista"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=15, choices=Kind.choices)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    institution = models.CharField(max_length=200, blank=True)
    biography = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name", "pk"]


class PublicationCredit(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="credits")
    person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="publication_links")
    kind = models.CharField(max_length=15, choices=Person.Kind.choices)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["publication", "person", "kind"], name="credit_person_unique"
            ),
            models.UniqueConstraint(
                fields=["publication", "kind", "position"], name="credit_order_unique"
            ),
        ]


class PublicationRevision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="revisions")
    document = models.ForeignKey(
        "documents.Document", on_delete=models.PROTECT, related_name="publication_revisions"
    )
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=Publication.Status.choices)
    snapshot = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        indexes = [models.Index(fields=["publication", "-created_at"])]
