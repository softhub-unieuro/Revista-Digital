from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class SiteSettings(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    name = models.CharField(max_length=200, default="Revista Científica de Psicologia")
    description = models.TextField(
        default="Publicação científica digital do curso de Psicologia do Centro Universitário UNIEURO."
    )
    issn = models.CharField(
        max_length=9,
        blank=True,
        validators=[RegexValidator(r"^\d{4}-\d{3}[\dX]$", "Informe o ISSN no formato 0000-0000.")],
    )
    ratings_enabled = models.BooleanField(default=True)
    downloads_enabled = models.BooleanField(default=True)
    public_archive_enabled = models.BooleanField(default=True)
    author_guidelines = models.TextField(blank=True)
    editorial_policy = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_text = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(id=1), name="single_site_settings")
        ]

    @classmethod
    def current(cls):
        return cls.objects.get_or_create(pk=1)[0]


class AuditEvent(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    actor_label = models.CharField(max_length=200, blank=True)
    target_label = models.CharField(max_length=255, blank=True)
    action = models.CharField(max_length=80)
    target = models.CharField(max_length=160)
    fields = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
