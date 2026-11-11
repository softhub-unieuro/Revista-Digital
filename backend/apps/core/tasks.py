from celery import shared_task
from django.db import connection


@shared_task
def infrastructure_probe():
    """Diagnóstico executado pelo worker real, sem modificar dados."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        ready = cursor.fetchone()[0] == 1
    return {"database": "ok" if ready else "unavailable"}
