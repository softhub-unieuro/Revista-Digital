from django.conf import settings
from django.db import DatabaseError, connection
from drf_spectacular.utils import extend_schema
from redis import Redis
from redis.exceptions import RedisError
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class LiveSerializer(serializers.Serializer):
    status = serializers.CharField()


class ReadySerializer(LiveSerializer):
    database = serializers.CharField()
    broker = serializers.CharField()


class LivenessView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(responses={200: LiveSerializer}, tags=["health"])
    def get(self, request):
        return Response({"status": "ok"})


class ReadinessView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(responses={200: ReadySerializer, 503: ReadySerializer}, tags=["health"])
    def get(self, request):
        database = broker = "ok"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except DatabaseError:
            database = "unavailable"
        try:
            client = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1)
            try:
                client.ping()
            finally:
                client.close()
        except (RedisError, ValueError):
            broker = "unavailable"
        healthy = database == broker == "ok"
        return Response(
            {"status": "ok" if healthy else "unavailable", "database": database, "broker": broker},
            status=200 if healthy else 503,
        )
