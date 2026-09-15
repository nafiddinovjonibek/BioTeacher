"""
Namunaviy 3D simulyatsiyalar va tajriba uchastkasi resurslari.

Faqat yo'q yozuvlar (slug bo'yicha, arxivdagilar ham hisobga olinadi) yaratiladi —
admin tahrirlagan yoki o'chirgan namuna qayta tiklanmaydi.
"""

from django.db import migrations


def seed(apps, schema_editor):
    from development.seed_data import PLOT_RESOURCES, SIMULATIONS

    Simulation = apps.get_model("development", "Simulation")
    PlotResource = apps.get_model("development", "PlotResource")
    Section = apps.get_model("content", "Section")

    for order, data in enumerate(SIMULATIONS):
        if Simulation.objects.filter(slug=data["slug"]).exists():
            continue
        Simulation.objects.create(
            slug=data["slug"], title=data["title"], summary=data["summary"], body=data["body"],
            parts=data["parts"], task=data["task"], visual=data["visual"], image_alt=data["alt"],
            section=Section.objects.filter(slug=data.get("section", ""), is_deleted=False).first(),
            order=order, is_active=True,
        )

    for order, data in enumerate(PLOT_RESOURCES):
        if PlotResource.objects.filter(slug=data["slug"]).exists():
            continue
        PlotResource.objects.create(
            slug=data["slug"], title=data["title"], kind=data["kind"], season=data["season"],
            grade=data["grade"], duration=data["duration"], summary=data["summary"], body=data["body"],
            order=order, is_active=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("development", "0001_initial"),
        ("content", "0003_alter_section_options_alter_section_title"),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
