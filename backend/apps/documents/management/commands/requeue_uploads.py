from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from apps.documents.models import Document
from apps.documents.tasks import process_document


class Command(BaseCommand):
    help = "Retoma uploads persistidos antes da inicialização do worker."

    def handle(self, *args, **options):
        pending = Document.objects.filter(
            Q(state="queued")
            | Q(state="processing", started_at__lt=timezone.now() - timedelta(seconds=130))
        )
        count = 0
        for pk in pending.values_list("pk", flat=True).iterator():
            process_document.delay(str(pk))
            count += 1
        self.stdout.write(f"{count} upload(s) encaminhado(s) ao worker.")
