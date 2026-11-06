import json
import logging
import re
import time
import uuid

from django.conf import settings

logger = logging.getLogger("http")


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        forwarded = request.headers.get("X-Request-ID", "") if settings.TRUST_PROXY_IP else ""
        identity = forwarded if re.fullmatch(r"[a-f0-9]{32}", forwarded) else uuid.uuid4().hex
        started = time.monotonic()
        response = self.get_response(request)
        response["X-Request-ID"] = identity
        if request.path.startswith("/api/"):
            # Sem query string, cookies, corpo, tokens ou cabeçalhos de autenticação.
            logger.info(
                json.dumps(
                    {
                        "request_id": identity,
                        "method": request.method,
                        "path": request.path,
                        "status": response.status_code,
                        "duration_ms": round((time.monotonic() - started) * 1000, 2),
                    }
                )
            )
        return response
