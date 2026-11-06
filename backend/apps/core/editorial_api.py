from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.accounts.permissions import IsAdministrator

from .audit import record
from .models import AuditEvent, SiteSettings


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        exclude = ["id"]
        read_only_fields = ["updated_at"]

    def validate_issn(self, value):
        if value:
            digits = value.replace("-", "")
            check = (11 - sum(int(n) * (8 - i) for i, n in enumerate(digits[:7])) % 11) % 11
            if digits[-1] != ("X" if check == 10 else str(check)):
                raise serializers.ValidationError("O dígito verificador do ISSN não é válido.")
        return value


class PublicSettingsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(responses=SettingsSerializer, tags=["settings"])
    def get(self, request):
        return Response(SettingsSerializer(SiteSettings.current()).data)


class AdminSettingsView(APIView):
    permission_classes = [IsAdministrator]

    @extend_schema(responses=SettingsSerializer, tags=["settings"])
    def get(self, request):
        return Response(SettingsSerializer(SiteSettings.current()).data)

    @extend_schema(request=SettingsSerializer, responses=SettingsSerializer, tags=["settings"])
    @transaction.atomic
    def patch(self, request):
        obj = SiteSettings.current()
        obj = SiteSettings.objects.select_for_update().get(pk=obj.pk)
        serializer = SettingsSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        record(request, "settings.update", obj, serializer.validated_data)
        return Response(serializer.data)


class AuditSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()
    actor_id = serializers.UUIDField(read_only=True, allow_null=True)

    def get_actor_name(self, obj) -> str:
        return obj.actor_label or (obj.actor.name if obj.actor else "Conta removida")

    class Meta:
        model = AuditEvent
        fields = [
            "id",
            "actor_id",
            "actor_name",
            "action",
            "target",
            "target_label",
            "fields",
            "created_at",
        ]


class AuditViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAdministrator]
    serializer_class = AuditSerializer
    queryset = AuditEvent.objects.select_related("actor").all()
