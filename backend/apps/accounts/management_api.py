from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

from apps.core.audit import record

from .permissions import IsAdministrator

User = get_user_model()


class ManagedUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)
    role_label = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "role",
            "role_label",
            "is_active",
            "password",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]

    def validate_email(self, value):
        value = value.strip().casefold()
        qs = User.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Este e-mail já está cadastrado.")
        return value

    def validate(self, attrs):
        if set(self.initial_data) - set(self.fields):
            raise serializers.ValidationError("Há campos não permitidos nesta operação.")
        password = attrs.get("password")
        if not self.instance and not password:
            raise serializers.ValidationError({"password": "Informe uma senha inicial."})
        if password is not None:
            candidate = User(
                email=attrs.get("email", getattr(self.instance, "email", "")),
                name=attrs.get("name", getattr(self.instance, "name", "")),
            )
            try:
                validate_password(password, user=candidate)
            except ValidationError as error:
                raise serializers.ValidationError({"password": error.messages}) from error
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserViewSet(ModelViewSet):
    permission_classes = [IsAdministrator]
    serializer_class = ManagedUserSerializer
    queryset = User.objects.order_by("name", "email", "pk")
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        if q := self.request.query_params.get("q"):
            qs = qs.filter(Q(name__unaccent__icontains=q) | Q(email__icontains=q))
        return qs

    @transaction.atomic
    def perform_create(self, serializer):
        user = serializer.save()
        record(self.request, "user.create", user, serializer.validated_data)

    @transaction.atomic
    def perform_update(self, serializer):
        # Todos os administradores são travados na mesma ordem para impedir duas
        # desativações/demissões concorrentes do último acesso administrativo.
        admins = list(
            User.objects.select_for_update()
            .filter(is_active=True)
            .filter(Q(role="admin") | Q(is_superuser=True))
            .order_by("pk")
        )
        user = User.objects.select_for_update().get(pk=serializer.instance.pk)
        role = serializer.validated_data.get("role", user.role)
        active = serializer.validated_data.get("is_active", user.is_active)
        if user.is_superuser and role != "admin":
            raise serializers.ValidationError(
                "O superusuário deve manter o perfil de administrador."
            )
        if (
            any(a.pk == user.pk for a in admins)
            and (not active or role != "admin")
            and len(admins) <= 1
        ):
            raise serializers.ValidationError("Mantenha pelo menos um administrador ativo.")
        serializer.instance = user
        updated = serializer.save()
        record(self.request, "user.update", updated, serializer.validated_data)
        if updated.pk == self.request.user.pk and "password" in serializer.validated_data:
            update_session_auth_hash(self.request, updated)
