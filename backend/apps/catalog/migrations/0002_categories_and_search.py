from django.contrib.postgres.operations import UnaccentExtension
from django.db import migrations


def seed(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    data = [
        ("Saúde Mental", "saude-mental", "brain"),
        ("Psicologia Escolar", "psicologia-escolar", "school"),
        ("Psicologia Familiar", "psicologia-familiar", "family"),
        ("Psicologia Social", "psicologia-social", "network"),
        ("Desenvolvimento Humano", "desenvolvimento-humano", "leaf"),
        ("Neuropsicologia", "neuropsicologia", "nodes"),
    ]
    for i, (name, slug, icon) in enumerate(data):
        Category.objects.get_or_create(
            slug=slug, defaults={"name": name, "icon": icon, "position": i}
        )


class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_initial")]
    operations = [UnaccentExtension(), migrations.RunPython(seed, migrations.RunPython.noop)]
