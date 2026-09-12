"""
«Muammoli vizual keyslar» boshlang'ich kontenti: rubrika va keyslar.

Faqat yo'q yozuvlar yaratiladi — admin keyin tahrirlagan matnlar qayta yozilmaydi.
Shu tufayli ishlab turgan saytda `migrate` ning o'zi yetarli, `seed_demo` shart emas.
"""

from django.db import migrations


def seed_visual_cases(apps, schema_editor):
    from assignments.seed_data import ASSIGNMENTS, RUBRICS

    Rubric = apps.get_model("assignments", "Rubric")
    Criterion = apps.get_model("assignments", "Criterion")
    Assignment = apps.get_model("assignments", "Assignment")
    Section = apps.get_model("content", "Section")

    cases = [data for data in ASSIGNMENTS if data["kind"] == "VISUAL"]
    rubrics = {}
    for data in RUBRICS:
        if data["slug"] not in {case["rubric"] for case in cases}:
            continue
        rubric, _ = Rubric.objects.get_or_create(
            slug=data["slug"], defaults={"title": data["title"], "description": data["description"]},
        )
        for order, criterion in enumerate(data["criteria"]):
            Criterion.objects.get_or_create(
                rubric=rubric, name=criterion["name"],
                defaults={"hint": criterion["hint"], "weight": criterion["weight"],
                          "max_score": criterion["max_score"], "level_descriptions": criterion["levels"],
                          "order": order},
            )
        rubrics[data["slug"]] = rubric

    for data in cases:
        if Assignment.objects.filter(slug=data["slug"]).exists():
            continue
        section = Section.objects.filter(slug=data.get("section", ""), is_deleted=False).first()
        Assignment.objects.create(
            slug=data["slug"], module=data["module"], kind=data["kind"], title=data["title"],
            body=data["body"], context_note=data.get("context", ""), component=data["component"],
            bloom_level=data["bloom"], rubric=rubrics[data["rubric"]],
            reference_solution=data.get("reference", ""), estimated_minutes=data["minutes"],
            difficulty=data["difficulty"], section=section, visual=data.get("visual", ""),
            image_alt=data.get("alt", ""), is_active=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("assignments", "0003_visual_cases"),
        ("content", "0003_alter_section_options_alter_section_title"),
    ]

    operations = [
        migrations.RunPython(seed_visual_cases, migrations.RunPython.noop),
    ]
