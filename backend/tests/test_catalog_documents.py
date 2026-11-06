import hashlib
from io import BytesIO
from unittest.mock import patch

import pytest
from apps.catalog.models import Category, Publication, PublicationCategory, Rating
from apps.documents.models import Document
from apps.documents.tasks import process_document
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from pypdf import PdfWriter
from reportlab.pdfgen import canvas

from tests.client import VersionedClient as APIClient

pytestmark = pytest.mark.django_db(transaction=True)


def pdf_bytes(pages=1, scanned=False):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    if scanned:
        image = Image.new("RGB", (320, 480), "#c9dfdf")
        from reportlab.lib.utils import ImageReader

        picture = ImageReader(image)
    for number in range(1, pages + 1):
        if scanned:
            pdf.drawImage(picture, 20, 20, 550, 780)
        else:
            pdf.drawString(50, 760, f"Revista de Psicologia - pagina {number}")
            pdf.linkURL("https://example.org/", (50, 730, 200, 750))
        pdf.showPage()
    pdf.save()
    return buffer.getvalue()


@pytest.fixture
def env(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    users = get_user_model()
    editor = users.objects.create_user(email="editor@test.com", password="pass", role="editor")
    collaborator = users.objects.create_user(email="collab@test.com", password="pass")
    other = users.objects.create_user(email="other@test.com", password="pass")
    category = Category.objects.create(name="Saúde", slug="saude")
    client = APIClient()
    client.force_authenticate(editor)
    return client, editor, collaborator, other, category


def document(owner, data=None):
    data = data or pdf_bytes()
    doc = Document.objects.create(
        owner=owner,
        file=ContentFile(data, name="revista.pdf"),
        original_name="revista.pdf",
        size_bytes=len(data),
    )
    process_document.apply(args=[str(doc.pk)]).get()
    doc.refresh_from_db()
    return doc


def publication(owner, category, doc, status="draft"):
    pub = Publication.objects.create(
        owner=owner,
        title="Saúde e inclusão",
        issue="N. 1",
        publication_date="2026-11-03",
        document=doc,
        status=status,
    )
    PublicationCategory.objects.create(publication=pub, category=category, position=0)
    return pub


@pytest.mark.parametrize(
    ("count", "scanned"), [(1, False), (2, False), (299, False), (300, False), (300, True)]
)
def test_real_pdf_pipeline(env, count, scanned):
    _, editor, *_ = env
    raw = pdf_bytes(count, scanned)
    doc = document(editor, raw)
    assert doc.state == "ready" and doc.page_count == count
    assert doc.sha256 == hashlib.sha256(raw).hexdigest()
    assert Image.open(doc.file.storage.path(doc.cover)).width <= 1000
    assert process_document.apply(args=[str(doc.pk)]).get() == {"state": "ready"}
    doc.refresh_from_db()
    assert doc.page_count == count


@pytest.mark.parametrize("kind", ["over_limit", "encrypted", "invalid", "empty"])
def test_rejects_invalid_pdf(env, kind):
    _, editor, *_ = env
    if kind == "over_limit":
        raw = pdf_bytes(301)
    elif kind == "invalid":
        raw = b"%PDF-1.7\ninvalid"
    else:
        writer = PdfWriter()
        if kind == "encrypted":
            writer.add_blank_page(width=100, height=100)
            writer.encrypt("secret")
        output = BytesIO()
        writer.write(output)
        raw = output.getvalue()
    doc = document(editor, raw)
    assert doc.state == "failed"
    assert not doc.cover
    assert doc.page_count == 0
    assert doc.error_message


def test_upload_is_async_and_validated(env, settings):
    client, editor, *_ = env
    with patch("apps.documents.views.process_document.delay") as enqueue:
        response = client.post(
            "/api/v1/admin/uploads",
            {"file": SimpleUploadedFile("file.pdf", pdf_bytes())},
            format="multipart",
        )
        assert response.status_code == 202
        enqueue.assert_called_once_with(response.data["id"])
        assert Document.objects.get(pk=response.data["id"]).state == "queued"
        assert (
            client.post(
                "/api/v1/admin/uploads",
                {"file": SimpleUploadedFile("a.pdf", b"not pdf")},
                format="multipart",
            ).status_code
            == 400
        )
        settings.MAX_PDF_BYTES = 10
        assert (
            client.post(
                "/api/v1/admin/uploads",
                {"file": SimpleUploadedFile("a.pdf", pdf_bytes())},
                format="multipart",
            ).status_code
            == 413
        )
    client.force_authenticate(None)
    assert client.post("/api/v1/admin/uploads", {}).status_code == 401


def test_draft_visibility_publish_archive_and_ranges(env):
    client, editor, collab, other, category = env
    raw = pdf_bytes(2)
    doc = document(collab, raw)
    pub = publication(collab, category, doc)
    public = APIClient()
    base = f"/api/v1/public/publications/{pub.slug}"
    assert public.get(base).status_code == 404
    assert public.get(base + "/file").status_code == 404
    client.force_authenticate(other)
    assert client.get(f"/api/v1/admin/jobs/{doc.pk}").status_code == 404
    assert client.get(f"/api/v1/admin/files/{doc.pk}").status_code == 404
    assert (
        client.patch(f"/api/v1/admin/publications/{pub.pk}", {"title": "stolen"}).status_code == 404
    )
    client.force_authenticate(collab)
    assert client.post(f"/api/v1/admin/publications/{pub.pk}/publish").status_code == 403
    assert (
        client.patch(f"/api/v1/admin/publications/{pub.pk}", {"title": "Revisão Saúde"}).status_code
        == 200
    )
    client.force_authenticate(editor)
    assert client.post(f"/api/v1/admin/publications/{pub.pk}/publish").status_code == 200
    assert public.get(base).status_code == 200
    full = public.get(base + "/file")
    assert b"".join(full.streaming_content) == raw
    assert full["Accept-Ranges"] == "bytes"
    assert int(public.head(base + "/file")["Content-Length"]) == len(raw)
    for range_value, expected in [
        ("bytes=0-9", raw[:10]),
        ("bytes=-20", raw[-20:]),
        ("bytes=100-", raw[100:]),
    ]:
        response = public.get(base + "/file", HTTP_RANGE=range_value)
        assert response.status_code == 206
        assert b"".join(response.streaming_content) == expected
    for value in ["bytes=999999-", "bytes=10-2", "bytes=-0", "bytes=0-2,4-6", "bytes=", "bad"]:
        assert public.get(base + "/file", HTTP_RANGE=value).status_code == 416
    assert public.get(base + "/garbage").status_code == 404
    download = public.get(base + "/download")
    assert "attachment" in download["Content-Disposition"]
    download.close()
    client.force_authenticate(collab)
    assert (
        client.patch(f"/api/v1/admin/publications/{pub.pk}", {"title": "change"}).status_code == 400
    )
    client.force_authenticate(editor)
    assert client.post(f"/api/v1/admin/publications/{pub.pk}/archive").status_code == 200
    assert public.get(base).status_code == 404
    assert public.get(base + "/file").status_code == 404
    assert client.post(f"/api/v1/admin/publications/{pub.pk}/restore").data["status"] == "draft"


def test_create_update_pagination_and_accent_search(env):
    client, editor, collab, other, category = env
    doc = document(editor)
    data = {
        "title": "Saúde em transformação",
        "issue": "N. 3",
        "publication_date": "2026-11-03",
        "description": "Inclusão escolar",
        "category_ids": [str(category.pk)],
        "document_id": str(doc.pk),
    }
    created = client.post("/api/v1/admin/publications", data, format="json")
    assert created.status_code == 201, created.data
    assert created.data["status"] == "draft" and created.data["page_count"] == 1
    pk, slug = created.data["id"], created.data["slug"]
    assert client.post(f"/api/v1/admin/publications/{pk}/publish").status_code == 200
    public = APIClient()
    for query in ["q=saude", "q=inclusao", "category=saude", "year=2026"]:
        response = public.get("/api/v1/public/publications?" + query)
        assert response.data["count"] == 1
    assert public.get("/api/v1/public/publications?year=oops").data["count"] == 0
    assert (
        client.patch(f"/api/v1/admin/publications/{pk}", {"title": "Novo título"}).data["slug"]
        == slug
    )
    client.force_authenticate(collab)
    assert client.post("/api/v1/admin/publications", data, format="json").status_code == 400
    client.force_authenticate(editor)
    bad = {**data, "category_ids": []}
    assert client.post("/api/v1/admin/publications", bad, format="json").status_code == 400
    other_doc = Document.objects.create(
        owner=editor, file=ContentFile(pdf_bytes(), name="pending.pdf")
    )
    assert (
        client.post(
            "/api/v1/admin/publications", {**data, "document_id": str(other_doc.pk)}, format="json"
        ).status_code
        == 400
    )
    for _i in range(23):
        publication(editor, category, doc, status="published")
    response = public.get("/api/v1/public/publications?page_size=5")
    assert (
        response.data["count"] == 24
        and len(response.data["results"]) == 5
        and response.data["next"]
    )


def test_rating_persists_and_updates_one_vote(env):
    _, editor, *_, category = env
    pub = publication(editor, category, document(editor), status="published")
    client = APIClient(enforce_csrf_checks=True)
    url = f"/api/v1/public/publications/{pub.slug}/rating"
    assert client.get(url).data["score"] is None
    assert client.post(url, {"score": 4}).status_code == 403
    csrf = client.get("/api/v1/auth/csrf").data["csrf_token"]
    for score in [4, 5]:
        assert client.post(url, {"score": score}, HTTP_X_CSRFTOKEN=csrf).status_code == 200
    assert Rating.objects.filter(publication=pub).count() == 1
    assert client.get(url).data["score"] == 5
    assert client.post(url, {"score": 9}, HTTP_X_CSRFTOKEN=csrf).status_code == 400


def test_custom_cover_and_reset(env):
    client, editor, *_ = env
    doc = document(editor)
    output = BytesIO()
    Image.new("RGB", (300, 400), "red").save(output, format="PNG")
    url = f"/api/v1/admin/jobs/{doc.pk}/cover"
    response = client.post(
        url,
        {"file": SimpleUploadedFile("cover.png", output.getvalue(), content_type="image/png")},
        format="multipart",
    )
    assert response.status_code == 200, response.data
    doc.refresh_from_db()
    assert Image.open(doc.file.storage.path(doc.cover)).getpixel((50, 50))[0] > 240
    assert client.post(url, {"reset": "true"}, format="multipart").status_code == 200
    assert (
        client.post(
            url, {"file": SimpleUploadedFile("bad.png", b"bad")}, format="multipart"
        ).status_code
        == 400
    )


def test_cannot_publish_unprocessed_document(env):
    client, editor, *_, category = env
    doc = Document.objects.create(owner=editor, file=ContentFile(pdf_bytes(), name="pending.pdf"))
    pub = publication(editor, category, doc)
    assert client.post(f"/api/v1/admin/publications/{pub.pk}/publish").status_code == 409


def test_creation_retries_are_idempotent(env):
    import uuid

    client, editor, *_rest, category = env
    data = {
        "title": "Idempotência",
        "issue": "N. 1",
        "publication_date": "2026-11-03",
        "document_id": str(document(editor).pk),
        "category_ids": [str(category.pk)],
        "client_key": str(uuid.uuid4()),
    }
    first = client.post("/api/v1/admin/publications", data, format="json")
    repeated = client.post("/api/v1/admin/publications", data, format="json")
    assert first.status_code == 201 and repeated.status_code == 200
    assert first.data["id"] == repeated.data["id"]
    assert Publication.objects.filter(client_key=data["client_key"]).count() == 1


def test_category_roles_and_deactivation(env):
    client, editor, collab, *_ = env
    response = client.post("/api/v1/admin/categories", {"name": "Tema novo", "slug": "tema-novo"})
    assert response.status_code == 201
    category_id = response.data["id"]
    client.force_authenticate(collab)
    assert (
        client.patch(f"/api/v1/admin/categories/{category_id}", {"name": "Outro"}).status_code
        == 403
    )
    client.force_authenticate(editor)
    assert (
        client.patch(
            f"/api/v1/admin/categories/{category_id}", {"active": False}, format="json"
        ).status_code
        == 200
    )
    assert APIClient().get("/api/v1/public/categories/tema-novo").status_code == 404


def test_broker_failure_is_durable_and_retryable(env):
    client, *_ = env
    with patch("apps.documents.views.process_document.delay", side_effect=ConnectionError):
        response = client.post(
            "/api/v1/admin/uploads",
            {"file": SimpleUploadedFile("revista.pdf", pdf_bytes())},
            format="multipart",
        )
    assert response.status_code == 503
    doc = Document.objects.get(pk=response.data["id"])
    assert doc.state == "queued" and doc.file.storage.exists(doc.file.name)
    with patch("apps.documents.views.process_document.delay") as enqueue:
        assert client.post(f"/api/v1/admin/jobs/{doc.pk}/retry").status_code == 202
        enqueue.assert_called_once_with(str(doc.pk))


def test_failed_replacement_keeps_published_file(env):
    client, editor, *_rest, category = env
    old = document(editor)
    pub = publication(editor, category, old, status="published")
    invalid = document(editor, pdf_bytes(301))
    response = client.patch(
        f"/api/v1/admin/publications/{pub.pk}", {"document_id": str(invalid.pk)}, format="json"
    )
    assert response.status_code == 400
    pub.refresh_from_db()
    assert pub.document_id == old.pk and pub.status == "published"
    public = APIClient().get(f"/api/v1/public/publications/{pub.slug}/file")
    assert hashlib.sha256(b"".join(public.streaming_content)).hexdigest() == old.sha256


def test_stale_processing_lease_can_resume(env):
    import uuid
    from datetime import timedelta

    from django.utils import timezone

    _, editor, *_ = env
    raw = pdf_bytes(2)
    doc = Document.objects.create(
        owner=editor,
        file=ContentFile(raw, name="interrupted.pdf"),
        state="processing",
        started_at=timezone.now() - timedelta(minutes=5),
        lease=uuid.uuid4(),
    )
    previous_lease = doc.lease
    assert process_document.apply(args=[str(doc.pk)]).get()["state"] == "ready"
    doc.refresh_from_db()
    assert doc.lease != previous_lease and doc.state == "ready" and doc.page_count == 2
