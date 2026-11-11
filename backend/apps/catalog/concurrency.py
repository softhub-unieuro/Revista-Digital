from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers
from rest_framework.exceptions import APIException


class EditConflict(APIException):
    status_code = 412
    default_detail = (
        "Esta edição foi alterada em outra sessão. Suas alterações não foram sobrescritas. "
        "Confira a versão atual antes de salvar novamente."
    )
    default_code = "edit_conflict"


class VersionRequired(APIException):
    status_code = 428
    default_detail = "Leia a edição atual e envie sua versão no cabeçalho If-Match."
    default_code = "version_required"


def edit_tag(publication):
    return f'"{publication.pk}:{publication.edit_version}"'


def check_version(request, publication):
    value = request.headers.get("If-Match")
    if value is None:
        raise VersionRequired()
    if value != edit_tag(publication):
        raise EditConflict()


version_parameter = OpenApiParameter(
    name="If-Match",
    location=OpenApiParameter.HEADER,
    required=True,
    type=str,
    description='Token da edição lida: "UUID:edit_version". Ausente: 428; antigo/inválido: 412.',
)


class VersionErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()
