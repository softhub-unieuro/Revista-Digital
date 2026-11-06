from django.core.management.base import BaseCommand, CommandError

from apps.core.tasks import infrastructure_probe


class Command(BaseCommand):
    help = "Comprova fila Redis → worker Celery → PostgreSQL."

    def handle(self, *args, **options):
        result = infrastructure_probe.delay().get(timeout=15)
        if result != {"database": "ok"}:
            raise CommandError("O worker não confirmou acesso ao banco.")
        self.stdout.write(self.style.SUCCESS("Redis, worker e PostgreSQL funcionando."))
