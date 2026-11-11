import uuid

from django.conf import settings
from django.db import models


def document_path(instance, filename):
    return f"documents/{instance.pk}.pdf"


class Document(models.Model):
    class State(models.TextChoices):
        QUEUED = "queued", "Aguardando"
        PROCESSING = "processing", "Processando"
        READY = "ready", "Pronto"
        FAILED = "failed", "Falhou"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    file = models.FileField(upload_to=document_path)
    original_name = models.CharField(max_length=255)
    state = models.CharField(max_length=20, choices=State.choices, default=State.QUEUED)
    page_count = models.PositiveIntegerField(default=0)
    size_bytes = models.PositiveBigIntegerField(default=0)
    sha256 = models.CharField(max_length=64, blank=True)
    cover = models.CharField(max_length=255, blank=True)
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.CharField(max_length=255, blank=True)
    lease = models.UUIDField(null=True, editable=False)
    started_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
