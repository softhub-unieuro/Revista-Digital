from django.conf import settings
from django.utils.crypto import salted_hmac
from redis import Redis
from redis.exceptions import RedisError
from rest_framework.exceptions import APIException
from rest_framework.throttling import BaseThrottle


class RatingUnavailable(APIException):
    status_code = 503
    default_detail = "Avaliações temporariamente indisponíveis. Tente novamente."


class RatingThrottle(BaseThrottle):
    def allow_request(self, request, view):
        if request.method != "POST":
            return True
        address = (
            request.META.get("HTTP_X_REAL_IP", "")
            if settings.TRUST_PROXY_IP
            else request.META.get("REMOTE_ADDR", "")
        )
        key = (
            "rating:" + salted_hmac("rating-limit", address + ":" + view.kwargs["slug"]).hexdigest()
        )
        client = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1)
        try:
            attempts = client.eval(
                "local n = redis.call('INCR', KEYS[1]); if n == 1 then redis.call('EXPIRE', KEYS[1], 300) end; return n",
                1,
                key,
            )
            return attempts <= settings.RATING_RATE_LIMIT
        except RedisError as error:
            raise RatingUnavailable() from error
        finally:
            client.close()

    def wait(self):
        return 300
