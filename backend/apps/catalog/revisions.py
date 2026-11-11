import uuid

from django.http import Http404

from apps.core.models import SiteSettings

from .models import Publication, PublicationRevision


def capture(request, publication):
    from .serializers import PublicationSerializer

    if not publication.document_id:
        return
    fresh = (
        Publication.objects.select_related("document")
        .prefetch_related("category_links__category", "credits__person")
        .get(pk=publication.pk)
    )
    values = PublicationSerializer(
        fresh, context={"private": True, "site": SiteSettings.current()}
    ).data
    fields = [
        "title",
        "issue",
        "publication_date",
        "description",
        "categories",
        "authors",
        "reviewers",
        "status",
    ]
    PublicationRevision.objects.create(
        publication=fresh,
        document=fresh.document,
        actor=request.user,
        status=fresh.status,
        snapshot={key: values[key] for key in fields},
    )


def resolve_document(publication, version, private=False):
    if not version:
        return publication.document, None
    try:
        identity = uuid.UUID(str(version))
    except (ValueError, TypeError) as error:
        raise Http404 from error
    if identity == publication.document_id:
        return publication.document, None
    revisions = publication.revisions.filter(
        document_id=identity, document__state="ready"
    ).select_related("document")
    if not private:
        revisions = revisions.filter(status="published")
    revision = revisions.first()
    if revision is None:
        raise Http404
    return revision.document, revision.snapshot
