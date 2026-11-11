from hashlib import sha256

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils.crypto import salted_hmac
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from redis import Redis
from redis.exceptions import RedisError
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class UserSerializer(serializers.Serializer):
    is_admin = serializers.SerializerMethodField()

    def get_is_admin(self, obj) -> bool:
        from .permissions import is_admin

        return is_admin(obj)

    id = serializers.UUIDField()
    email = serializers.EmailField()
    name = serializers.CharField()
    role = serializers.CharField()
    role_label = serializers.CharField(source="get_role_display")


class SessionSerializer(serializers.Serializer):
    authenticated = serializers.BooleanField()
    user = UserSerializer(allow_null=True)


class CredentialsSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class CsrfSerializer(serializers.Serializer):
    csrf_token = serializers.CharField()


class ErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()


def session_payload(user):
    return {
        "authenticated": user.is_authenticated,
        "user": UserSerializer(user).data if user.is_authenticated else None,
    }


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(responses=CsrfSerializer, tags=["authentication"])
    def get(self, request):
        return Response({"csrf_token": get_token(request)})


class SessionView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=SessionSerializer, tags=["authentication"])
    def get(self, request):
        return Response(session_payload(request.user))


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=CredentialsSerializer,
        responses={
            200: SessionSerializer,
            401: ErrorSerializer,
            429: ErrorSerializer,
            503: ErrorSerializer,
        },
        tags=["authentication"],
    )
    def post(self, request):
        credentials = CredentialsSerializer(data=request.data)
        credentials.is_valid(raise_exception=True)
        email = credentials.validated_data["email"].strip().casefold()
        identity = email + ":" + request.META.get("REMOTE_ADDR", "")
        key = (
            "login:" + salted_hmac("login-limit", sha256(identity.encode()).hexdigest()).hexdigest()
        )
        client = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1)
        try:
            attempts = client.eval(
                "local n = redis.call('INCR', KEYS[1]); "
                "if n == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end; return n",
                1,
                key,
                300,
            )
            if attempts > 10:
                return Response(
                    {"detail": "Muitas tentativas. Aguarde alguns minutos."}, status=429
                )
            user = authenticate(
                request, email=email, password=credentials.validated_data["password"]
            )
            if user is None:
                return Response({"detail": "E-mail ou senha incorretos."}, status=401)
            client.delete(key)
            login(request, user)
            return Response(session_payload(user))
        except RedisError:
            return Response(
                {"detail": "Acesso temporariamente indisponível. Tente novamente."}, status=503
            )
        finally:
            client.close()


@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=None, responses={204: None}, tags=["authentication"])
    def post(self, request):
        logout(request)
        return Response(status=204)
