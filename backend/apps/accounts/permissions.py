from rest_framework.permissions import BasePermission


def is_admin(user):
    return bool(
        user.is_authenticated and user.is_active and (user.is_superuser or user.role == "admin")
    )


class IsAdministrator(BasePermission):
    message = "Esta ação exige acesso de administrador."

    def has_permission(self, request, view):
        return is_admin(request.user)
