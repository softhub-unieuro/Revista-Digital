from django.db import transaction
from django.db.models import Count, Q
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.audit import record

from .models import Person
from .permissions import can_publish


class PersonSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Person
        fields = ["id", "kind", "name", "email", "institution", "biography", "active", "count"]

    def validate_kind(self, value):
        if self.instance and self.instance.kind != value:
            raise serializers.ValidationError("O tipo de cadastro não pode ser alterado.")
        return value


class PersonViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PersonSerializer
    queryset = Person.objects.annotate(
        count=Count("publication_links__publication", distinct=True)
    ).order_by("name", "pk")
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        if kind := self.request.query_params.get("kind"):
            qs = qs.filter(kind=kind)
        if q := self.request.query_params.get("q"):
            qs = qs.filter(Q(name__unaccent__icontains=q) | Q(institution__unaccent__icontains=q))
        return qs

    @transaction.atomic
    def perform_create(self, serializer):
        if not can_publish(self.request.user):
            raise PermissionDenied()
        person = serializer.save()
        record(self.request, "person.create", person, serializer.validated_data)

    @transaction.atomic
    def perform_update(self, serializer):
        if not can_publish(self.request.user):
            raise PermissionDenied()
        person = serializer.save()
        record(self.request, "person.update", person, serializer.validated_data)
