import pytest
from apps.core import views
from django.db import OperationalError


def test_liveness_does_not_require_database(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_readiness_checks_real_postgres_and_redis(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok", "broker": "ok"}


@pytest.mark.django_db
def test_readiness_fails_without_leaking_connection_details(client, monkeypatch):
    def fail():
        raise OperationalError("private database credentials")

    monkeypatch.setattr(views.connection, "cursor", fail)
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["database"] == "unavailable"
    assert b"credentials" not in response.content
