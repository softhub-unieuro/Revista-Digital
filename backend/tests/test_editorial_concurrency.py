from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from apps.catalog.concurrency import edit_tag
from apps.core.models import AuditEvent
from django.contrib.auth import get_user_model
from django.db import connections
from rest_framework.test import APIClient

from tests.test_editorial_admin import ready_publication

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def edition(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    editor = get_user_model().objects.create_user(
        "concurrency@test.local", "Test-only.Strong.923", name="Editor", role="editor"
    )
    pub = ready_publication(editor)
    client = APIClient()
    client.force_authenticate(editor)
    return client, editor, pub


def test_missing_and_invalid_versions_do_not_change_publication(edition):
    client, _, pub = edition
    url = f"/api/v1/admin/publications/{pub.pk}"
    row = client.get(url).data
    assert row["edit_version"] == 1
    for tag, status in [(None, 428), ('"old"', 412), ("*", 412), ("W/" + edit_tag(pub), 412)]:
        headers = {"HTTP_IF_MATCH": tag} if tag is not None else {}
        assert (
            client.patch(url, {"title": "Perdido"}, format="json", **headers).status_code == status
        )
    pub.refresh_from_db()
    assert pub.title == row["title"] and pub.edit_version == 1
    assert not AuditEvent.objects.filter(action="publication.update").exists()


def test_stale_editor_keeps_saved_metadata_and_history(edition):
    client, _, pub = edition
    url = f"/api/v1/admin/publications/{pub.pk}"
    token = edit_tag(pub)
    first = client.patch(url, {"title": "Primeiro editor"}, HTTP_IF_MATCH=token)
    assert first.status_code == 200 and first.data["edit_version"] == 2
    history_count = pub.revisions.count()
    second = client.patch(url, {"title": "Segundo editor"}, HTTP_IF_MATCH=token)
    assert second.status_code == 412
    pub.refresh_from_db()
    assert pub.title == "Primeiro editor" and pub.revisions.count() == history_count
    assert client.patch(url, {"title": "Revisado"}, HTTP_IF_MATCH=edit_tag(pub)).status_code == 200


@pytest.mark.parametrize("action", ["publish", "archive", "restore"])
def test_editorial_actions_require_current_version(edition, action):
    client, _, pub = edition
    url = f"/api/v1/admin/publications/{pub.pk}/{action}"
    assert client.post(url).status_code == 428
    token = edit_tag(pub)
    assert client.post(url, HTTP_IF_MATCH=token).status_code == 200
    assert client.post(url, HTTP_IF_MATCH=token).status_code == 412
    pub.refresh_from_db()
    assert pub.edit_version == 2


def test_simultaneous_save_and_archive_have_exactly_one_winner(edition):
    _, editor, pub = edition
    token = edit_tag(pub)
    barrier = Barrier(2)

    def change(archive):
        try:
            actor = get_user_model().objects.get(pk=editor.pk)
            client = APIClient()
            client.force_authenticate(actor)
            barrier.wait(timeout=10)
            url = f"/api/v1/admin/publications/{pub.pk}"
            response = (
                client.post(url + "/archive", HTTP_IF_MATCH=token)
                if archive
                else client.patch(url, {"title": "Alteração concorrente"}, HTTP_IF_MATCH=token)
            )
            return response.status_code
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(change, [True, False]))
    assert sorted(results) == [200, 412]
    pub.refresh_from_db()
    assert pub.edit_version == 2
    assert (
        AuditEvent.objects.filter(action__in=["publication.update", "publication.archive"]).count()
        == 1
    )
