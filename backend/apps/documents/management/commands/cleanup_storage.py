import re
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.documents.models import Document


class Command(BaseCommand):
    help = "Lista arquivos expirados sem uso. Só remove com --apply; publicações vinculadas são preservadas."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=30)
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        if options["days"] < 1:
            raise CommandError("A retenção mínima é de um dia.")
        cutoff = timezone.now() - timedelta(days=options["days"])
        count = 0
        candidates = (
            Document.objects.filter(
                created_at__lt=cutoff, state__in=["ready", "failed"], publication__isnull=True
            )
            .filter(publication_revisions__isnull=True)
            .values_list("pk", flat=True)
        )
        for pk in list(candidates):
            with transaction.atomic():
                doc = Document.objects.select_for_update().filter(pk=pk).first()
                if (
                    doc is None
                    or doc.publication_set.exists()
                    or doc.publication_revisions.exists()
                ):
                    continue
                count += 1
                if options["apply"]:
                    # Primeiro remover o registro. Arquivos que falhem ao remover
                    # continuam detectáveis como órfãos na próxima execução.
                    filename, cover = doc.file.name, doc.cover
                    storage = doc.file.storage
                    doc.delete()
                    storage.delete(filename)
                    if cover:
                        storage.delete(cover)
        references = set()
        for filename, cover in Document.objects.values_list("file", "cover").iterator():
            references.update([filename, cover])
        orphan_count = 0
        root = Path(settings.MEDIA_ROOT)
        for folder, pattern in [
            ("documents", r"[0-9a-f-]{36}\.pdf"),
            ("covers", r"[0-9a-f-]{36}-[0-9a-f-]{36}\.jpg"),
        ]:
            directory = root / folder
            if not directory.is_dir():
                continue
            for file in directory.iterdir():
                if file.is_symlink() or not file.is_file() or not re.fullmatch(pattern, file.name):
                    continue
                if (
                    file.relative_to(root).as_posix() in references
                    or file.stat().st_mtime >= cutoff.timestamp()
                ):
                    continue
                orphan_count += 1
                if options["apply"]:
                    file.unlink(missing_ok=True)
        self.stdout.write(
            f"{'Removidos' if options['apply'] else 'Candidatos (simulação)'}: {count} documentos sem vínculo e {orphan_count} arquivos órfãos."
        )
