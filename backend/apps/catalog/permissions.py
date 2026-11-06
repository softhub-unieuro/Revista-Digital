from rest_framework.permissions import BasePermission


def can_publish(user):
    return bool(
        user.is_authenticated
        and user.is_active
        and (user.is_superuser or user.role in {"admin", "editor"})
    )


def can_edit(user, publication):
    return can_publish(user) or (
        user.is_authenticated
        and user.is_active
        and publication.owner_id == user.pk
        and publication.status == "draft"
    )


class PublicArchiveAvailable(BasePermission):
    message = "O acervo público está temporariamente indisponível."

    def has_permission(self, request, view):
        from apps.core.models import SiteSettings

        if not SiteSettings.current().public_archive_enabled:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(self.message)
        return True
