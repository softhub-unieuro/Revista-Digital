import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def account():
    return get_user_model().objects.create_user(
        f"{uuid.uuid4()}@example.test", "valid-password-9", name="Professora"
    )


@pytest.fixture
def api():
    return APIClient(enforce_csrf_checks=True)


def token(api):
    return api.get("/api/v1/auth/csrf").json()["csrf_token"]


def test_login_requires_csrf_even_for_anonymous_requests(api, account):
    response = api.post(
        "/api/v1/auth/login",
        {"email": account.email, "password": "valid-password-9"},
        format="json",
    )
    assert response.status_code == 403
    assert api.get("/api/v1/auth/me").json()["authenticated"] is False


def test_login_restores_session_and_logout_invalidates_it(api, account):
    csrf = token(api)
    response = api.post(
        "/api/v1/auth/login",
        {"email": account.email.upper(), "password": "valid-password-9"},
        format="json",
        HTTP_X_CSRFTOKEN=csrf,
    )
    assert response.status_code == 200
    assert response.json()["user"]["id"] == str(account.pk)
    assert "password" not in response.content.decode()
    assert api.get("/api/v1/auth/me").json()["authenticated"] is True
    assert api.post("/api/v1/auth/logout").status_code == 403
    csrf = token(api)
    assert api.post("/api/v1/auth/logout", HTTP_X_CSRFTOKEN=csrf).status_code == 204
    assert api.get("/api/v1/auth/me").json() == {"authenticated": False, "user": None}


def test_bad_password_and_inactive_user_do_not_get_sessions(api, account):
    csrf = token(api)
    payload = {"email": account.email, "password": "wrong-password"}
    assert (
        api.post("/api/v1/auth/login", payload, format="json", HTTP_X_CSRFTOKEN=csrf).status_code
        == 401
    )
    account.is_active = False
    account.save()
    payload["password"] = "valid-password-9"
    assert (
        api.post("/api/v1/auth/login", payload, format="json", HTTP_X_CSRFTOKEN=csrf).status_code
        == 401
    )


def test_repeated_attempts_are_limited_by_server(api, account):
    csrf = token(api)
    payload = {"email": account.email, "password": "wrong-password"}
    for _ in range(10):
        assert (
            api.post(
                "/api/v1/auth/login", payload, format="json", HTTP_X_CSRFTOKEN=csrf
            ).status_code
            == 401
        )
    assert (
        api.post("/api/v1/auth/login", payload, format="json", HTTP_X_CSRFTOKEN=csrf).status_code
        == 429
    )
