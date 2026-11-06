import json
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from io import BytesIO
from unittest.mock import patch

import pytest
from apps.catalog.models import Category, Publication, PublicationCategory
from apps.core.models import AuditEvent
from apps.documents.models import Document
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.db import connections
from django.utils import timezone
from pypdf import PdfWriter
from redis.exceptions import RedisError

from tests.client import VersionedClient as APIClient

pytestmark = pytest.mark.django_db(transaction=True)
PASSWORD = "Editorial-test-Strong.5832"


@pytest.fixture
def setup(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    users = get_user_model()
    admin = users.objects.create_user("admin@test.local", PASSWORD, name="Admin", role="admin")
    editor = users.objects.create_user("editor@test.local", PASSWORD, name="Editor", role="editor")
    collab = users.objects.create_user("collab@test.local", PASSWORD, name="Colaborador")
    client = APIClient()
    client.force_authenticate(admin)
    return client, admin, editor, collab


def ready_publication(owner):
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=300)
    writer.write(output)
    doc = Document.objects.create(
        owner=owner,
        file=ContentFile(output.getvalue(), name="revista.pdf"),
        original_name="revista.pdf",
        state="ready",
        page_count=1,
    )
    pub = Publication.objects.create(
        owner=owner,
        title="Revista de teste",
        issue="N. 1",
        publication_date="2026-11-03",
        document=doc,
        status="published",
    )
    category = Category.objects.create(name="Saúde", slug="saude")
    PublicationCategory.objects.create(publication=pub, category=category, position=0)
    return pub


@pytest.mark.parametrize("role", ["editor", "collaborator", None])
def test_sensitive_endpoints_are_admin_only(setup, role):
    client, _admin, editor, collab = setup
    client.force_authenticate(editor if role == "editor" else collab if role else None)
    for url in ["/api/v1/admin/users", "/api/v1/admin/settings", "/api/v1/admin/audit"]:
        assert client.get(url).status_code == (403 if role else 401)
    assert client.post(
        "/api/v1/admin/users",
        {"email": "escalation@test.local", "password": PASSWORD, "name": "X", "role": "admin"},
    ).status_code == (403 if role else 401)


def test_user_crud_password_and_casefold_email(setup):
    client, *_ = setup
    payload = {
        "email": "NEW@EXAMPLE.TEST",
        "name": "Nova pessoa",
        "role": "editor",
        "password": PASSWORD,
    }
    response = client.post("/api/v1/admin/users", payload, format="json")
    assert response.status_code == 201, response.data
    assert "password" not in response.data
    user = get_user_model().objects.get(pk=response.data["id"])
    assert user.check_password(PASSWORD) and user.email == "new@example.test"
    assert not user.is_staff and not user.is_superuser
    assert (
        client.post(
            "/api/v1/admin/users", {**payload, "email": "new@example.test"}, format="json"
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/v1/admin/users",
            {**payload, "email": "other@test.local", "is_superuser": True},
            format="json",
        ).status_code
        == 400
    )
    assert (
        client.patch(
            f"/api/v1/admin/users/{user.pk}", {"is_active": False}, format="json"
        ).status_code
        == 200
    )
    user.refresh_from_db()
    assert not user.is_active
    assert client.delete(f"/api/v1/admin/users/{user.pk}").status_code == 405
    assert PASSWORD not in json.dumps(
        [
            {"action": e.action, "target": e.target, "fields": e.fields}
            for e in AuditEvent.objects.all()
        ]
    )
    assert not any("password" in event.fields for event in AuditEvent.objects.all())


def test_password_policy_and_last_admin_guard(setup):
    client, admin, *_ = setup
    for change in [{"is_active": False}, {"role": "collaborator"}]:
        assert (
            client.patch(f"/api/v1/admin/users/{admin.pk}", change, format="json").status_code
            == 400
        )
    assert (
        client.post(
            "/api/v1/admin/users",
            {"email": "new@test.local", "name": "Nova", "password": "12345678"},
            format="json",
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/v1/admin/users", {"email": "new@test.local", "name": "Nova"}, format="json"
        ).status_code
        == 400
    )


def test_concurrent_last_admin_deactivations_keep_access(setup):
    _, admin, *_ = setup
    second = get_user_model().objects.create_user(
        "admin2@test.local", PASSWORD, name="Outro", role="admin"
    )

    def disable(pk):
        try:
            client = APIClient()
            client.force_authenticate(get_user_model().objects.get(pk=pk))
            return client.patch(
                f"/api/v1/admin/users/{pk}", {"is_active": False}, format="json"
            ).status_code
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = list(pool.map(disable, [admin.pk, second.pk]))
    assert sorted(codes) == [200, 400]
    assert get_user_model().objects.filter(role="admin", is_active=True).count() == 1


def test_person_links_kinds_order_and_history(setup):
    client, admin, editor, collab = setup
    client.force_authenticate(editor)
    people = []
    for kind, name in [("author", "Autora Ágata"), ("author", "Autor B"), ("reviewer", "Revisora")]:
        response = client.post(
            "/api/v1/admin/people",
            {"kind": kind, "name": name, "email": "private@example.test", "institution": "UNIEURO"},
            format="json",
        )
        assert response.status_code == 201
        people.append(response.data["id"])
    pub = ready_publication(editor)
    url = f"/api/v1/admin/publications/{pub.pk}"
    linked = client.patch(
        url, {"author_ids": people[:2], "reviewer_ids": [people[2]]}, format="json"
    )
    assert linked.status_code == 200, linked.data
    assert [p["id"] for p in linked.data["authors"]] == people[:2]
    assert client.patch(url, {"author_ids": [people[2]]}, format="json").status_code == 400
    assert (
        client.patch(url, {"author_ids": [people[0], people[0]]}, format="json").status_code == 400
    )
    assert (
        client.patch(f"/api/v1/admin/people/{people[0]}", {"kind": "reviewer"}).status_code == 400
    )
    client.patch(f"/api/v1/admin/people/{people[0]}", {"active": False}, format="json")
    assert client.patch(url, {"author_ids": people[:2]}, format="json").status_code == 200
    public = APIClient().get(f"/api/v1/public/publications/{pub.slug}")
    assert "email" not in public.data["authors"][0]
    assert client.get("/api/v1/admin/people?kind=author&q=agata").data["count"] == 1
    client.force_authenticate(collab)
    assert (
        client.post("/api/v1/admin/people", {"kind": "author", "name": "Fake"}).status_code == 403
    )
    assert client.get("/api/v1/admin/people").status_code == 200


def test_settings_are_persisted_and_enforced_server_side(setup):
    client, admin, *_ = setup
    pub = ready_publication(admin)
    public = APIClient()
    url = f"/api/v1/public/publications/{pub.slug}"
    assert public.get(url).data["download_url"]
    settings_url = "/api/v1/admin/settings"
    result = client.patch(
        settings_url,
        {"name": "Revista acadêmica", "downloads_enabled": False, "ratings_enabled": False},
        format="json",
    )
    assert result.status_code == 200
    assert public.get("/api/v1/public/settings").data["name"] == "Revista acadêmica"
    assert public.get(url).data["download_url"] is None
    assert public.get(url + "/download").status_code == 403
    reader = public.get(url + "/file")
    assert reader.status_code == 200
    reader.close()
    assert public.get(url + "/rating").status_code == 403
    assert client.patch(settings_url, {"issn": "2675-0000"}, format="json").status_code == 400
    assert client.patch(settings_url, {"issn": "0317-8471"}, format="json").status_code == 200
    client.patch(settings_url, {"public_archive_enabled": False}, format="json")
    for suffix in ["", "/file", "/cover", "/download", "/rating"]:
        assert public.get(url + suffix).status_code == 403
    private = client.get(f"/api/v1/admin/files/{pub.document_id}")
    assert private.status_code == 200
    private.close()
    assert public.get("/api/v1/public/settings").status_code == 200


def test_votes_are_limited_and_redis_failure_is_useful(setup, settings):
    _, admin, *_ = setup
    pub = ready_publication(admin)
    public = APIClient()
    url = f"/api/v1/public/publications/{pub.slug}/rating"
    settings.RATING_RATE_LIMIT = 1
    public.get(url)
    assert public.post(url, {"score": 4}).status_code == 200
    assert public.post(url, {"score": 5}).status_code == 429
    with patch("apps.catalog.throttles.Redis.from_url") as redis:
        redis.return_value.eval.side_effect = RedisError
        assert public.post(url, {"score": 5}).status_code == 503


def test_x_accel_authorizes_before_delegating(setup, settings):
    client, admin, *_ = setup
    pub = ready_publication(admin)
    settings.USE_X_ACCEL_REDIRECT = True
    public = APIClient()
    url = f"/api/v1/public/publications/{pub.slug}/file"
    response = public.get(url)
    assert (
        response.status_code == 200
        and response["X-Accel-Redirect"] == f"/_protected/documents/{pub.document_id}.pdf"
    )
    assert public.get(url, HTTP_RANGE="bytes=999999-").status_code == 416
    pub.status = "archived"
    pub.save()
    assert public.get(url).status_code == 404
    assert client.get(f"/api/v1/admin/files/{pub.document_id}")["X-Accel-Redirect"]


def test_storage_cleanup_is_dry_by_default_and_preserves_publications(setup, settings):
    _, admin, *_ = setup
    pub = ready_publication(admin)
    unused = Document.objects.create(
        owner=admin, file=ContentFile(b"failed", name="unused.pdf"), state="failed"
    )
    cutoff = timezone.now() - timedelta(days=40)
    Document.objects.filter(pk__in=[unused.pk, pub.document_id]).update(created_at=cutoff)
    orphan = settings.MEDIA_ROOT / "covers" / f"{uuid.uuid4()}-{uuid.uuid4()}.jpg"
    orphan.parent.mkdir(parents=True, exist_ok=True)
    orphan.write_bytes(b"orphan")
    os.utime(orphan, (cutoff.timestamp(), cutoff.timestamp()))
    call_command("cleanup_storage")
    assert unused.file.storage.exists(unused.file.name) and orphan.exists()
    call_command("cleanup_storage", apply=True)
    assert not Document.objects.filter(pk=unused.pk).exists() and not orphan.exists()
    assert Document.objects.filter(pk=pub.document_id).exists()
    assert pub.document.file.storage.exists(pub.document.file.name)


def test_deactivated_user_session_expires(setup):
    _, admin, editor, *_ = setup
    client = APIClient(enforce_csrf_checks=True)
    csrf = client.get("/api/v1/auth/csrf").data["csrf_token"]
    assert (
        client.post(
            "/api/v1/auth/login",
            {"email": editor.email, "password": PASSWORD},
            format="json",
            HTTP_X_CSRFTOKEN=csrf,
        ).status_code
        == 200
    )
    editor.is_active = False
    editor.save()
    assert client.get("/api/v1/admin/publications").status_code == 401
    assert client.get("/api/v1/auth/me").data["user"] is None


def test_catalog_summary_uses_only_published_ready_data(setup):
    _, admin, *_ = setup
    pub = ready_publication(admin)
    public = APIClient()
    summary = public.get("/api/v1/public/catalog")
    assert summary.status_code == 200 and summary.data["years"] == [2026]
    assert summary.data["total"] == 1 and summary.data["featured"]["id"] == str(pub.pk)
    pub.status = "draft"
    pub.save()
    assert public.get("/api/v1/public/catalog").data == {"total": 0, "years": [], "featured": None}


def test_audit_snapshots_survive_name_changes_and_request_ids_are_safe(setup):
    client, admin, *_ = setup
    response = client.patch(
        "/api/v1/admin/settings",
        {"description": "Nova descrição"},
        format="json",
        HTTP_X_REQUEST_ID="untrusted",
    )
    assert response.status_code == 200 and len(response["X-Request-ID"]) == 32
    event = AuditEvent.objects.get(action="settings.update")
    assert event.actor_label == "Admin" and event.target_label
    admin.name = "Renomeado"
    admin.save()
    assert client.get("/api/v1/admin/audit").data["results"][0]["actor_name"] == "Admin"


def test_replacing_pdf_keeps_versioned_readers_and_history(setup):
    client, admin, _, collab = setup
    pub = ready_publication(admin)
    old = pub.document
    original = old.file.read()
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=400)
    writer.write(output)
    new = Document.objects.create(
        owner=admin,
        file=ContentFile(output.getvalue(), name="replacement.pdf"),
        state="ready",
        original_name="replacement.pdf",
        page_count=1,
    )
    result = client.patch(
        f"/api/v1/admin/publications/{pub.pk}",
        {"document_id": str(new.pk), "title": "Edição corrigida"},
        format="json",
    )
    assert result.status_code == 200
    public = APIClient()
    url = f"/api/v1/public/publications/{pub.slug}/file"
    previous = public.get(url + "?v=" + str(old.pk))
    assert b"".join(previous.streaming_content) == original
    latest = public.get(url + "?v=" + str(new.pk))
    assert b"".join(latest.streaming_content) == output.getvalue()
    metadata = public.get(f"/api/v1/public/publications/{pub.slug}?document={old.pk}")
    assert metadata.data["title"] == "Revista de teste" and metadata.data[
        "document_version"
    ] == str(old.pk)
    assert public.get(url + "?v=" + str(uuid.uuid4())).status_code == 404
    assert public.get(url + "?v=invalid").status_code == 404
    history = client.get(f"/api/v1/admin/publications/{pub.pk}/revisions")
    assert history.status_code == 200 and history.data["count"] == 2
    assert all("version=" in item["preview_url"] for item in history.data["results"])
    Document.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=40))
    call_command("cleanup_storage", apply=True)
    assert Document.objects.filter(pk=old.pk).exists() and old.file.storage.exists(old.file.name)
    # Editor pode anexar arquivo à edição do colaborador sem quebrar o preview dele.
    pub.owner = collab
    pub.save()
    client.force_authenticate(collab)
    read = client.get(f"/api/v1/admin/files/{new.pk}")
    assert read.status_code == 200
    read.close()
    assert client.post(f"/api/v1/admin/jobs/{new.pk}/retry").status_code == 404
    client.force_authenticate(admin)
    client.post(f"/api/v1/admin/publications/{pub.pk}/archive")
    assert public.get(url + "?v=" + str(old.pk)).status_code == 404
