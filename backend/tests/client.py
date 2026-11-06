"""Cliente dos testes de fluxo: lê a versão atual antes de uma escrita editorial.

Os testes de concorrência usam APIClient diretamente e conservam tokens antigos.
"""

import re

from apps.catalog.models import Publication
from rest_framework.test import APIClient


class VersionedClient(APIClient):
    def generic(self, method, path, *args, **kwargs):
        match = re.fullmatch(
            r"/api/v1/admin/publications/([0-9a-f-]{36})(?:/(publish|archive|restore))?", path
        )
        if match and method in {"PATCH", "POST"} and "HTTP_IF_MATCH" not in kwargs:
            obj = Publication.objects.filter(pk=match[1]).first()
            if obj:
                kwargs["HTTP_IF_MATCH"] = f'"{obj.pk}:{obj.edit_version}"'
        return super().generic(method, path, *args, **kwargs)
