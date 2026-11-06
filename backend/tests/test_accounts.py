import uuid

import pytest
from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError, transaction

pytestmark = pytest.mark.django_db


def test_user_has_uuid_and_authenticates_by_normalized_email():
    user = get_user_model().objects.create_user(
        "  Professor@UNIEURO.edu.br  ", "test-password", name="Professor"
    )
    assert isinstance(user.pk, uuid.UUID)
    assert user.email == "professor@unieuro.edu.br"
    assert user.role == "collaborator"
    assert user.password != "test-password"
    assert authenticate(email=user.email, password="test-password") == user


def test_database_rejects_case_insensitive_duplicates():
    model = get_user_model()
    model.objects.create_user("editor@example.com", "test-password")
    with transaction.atomic(), pytest.raises(IntegrityError):
        model.objects.bulk_create([model(email="EDITOR@example.com")])


def test_superuser_creation_and_flags():
    user = get_user_model().objects.create_superuser(
        "admin@example.com", "test-password", name="Admin"
    )
    assert user.role == "admin" and user.is_staff and user.is_superuser
    with pytest.raises(ValueError):
        get_user_model().objects.create_superuser(
            "other@example.com", "test-password", is_staff=False
        )
