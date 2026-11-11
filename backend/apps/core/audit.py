from .models import AuditEvent


def record(request, action, instance, fields=()):
    # Guardar identificação e nomes dos campos; nunca valores de senha ou payloads.
    changed = set(fields) - {"password", "client_key"}
    if "password" in fields:
        changed.add("credential")
    return AuditEvent.objects.create(
        actor=request.user if request.user.is_authenticated else None,
        actor_label=(request.user.name or request.user.email)
        if request.user.is_authenticated
        else "Operação técnica",
        target_label=str(
            getattr(instance, "title", "")
            or getattr(instance, "name", "")
            or getattr(instance, "original_name", "")
            or instance._meta.verbose_name
        )[:255],
        action=action,
        target=f"{instance._meta.label_lower}:{instance.pk}",
        fields=sorted(changed),
    )
