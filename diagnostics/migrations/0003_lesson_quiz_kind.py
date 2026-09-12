"""
Dars mustahkamlash testlarini `QUIZ` turiga ko'chiradi va shu testlar
noto'g'ri hosil qilgan kesim o'lchovlarini tozalaydi (SR-06).

Ilgari dars testi ham `TEST` turida, `cut=INITIAL` bilan saqlanardi; uni
yechgan talabaning boshlang'ich diagnostika o'lchovi bekor bo'lib, o'rniga
4 savollik test natijasi yozilardi — bu tadqiqot solishtiruvini buzardi.
"""

from django.db import migrations


def forwards(apps, schema_editor):
    Questionnaire = apps.get_model("diagnostics", "Questionnaire")
    Attempt = apps.get_model("diagnostics", "Attempt")
    Measurement = apps.get_model("diagnostics", "Measurement")
    Lesson = apps.get_model("content", "Lesson")

    quiz_ids = set(Lesson.objects.exclude(quiz=None).values_list("quiz_id", flat=True))
    quiz_ids |= set(
        Questionnaire.objects.filter(slug__startswith="quiz-").values_list("id", flat=True)
    )
    if not quiz_ids:
        return
    Questionnaire.objects.filter(id__in=quiz_ids).update(kind="QUIZ")

    # Dars testidan tug'ilgan o'lchovlarni olib tashlaymiz.
    sources = [
        f"attempt:{pk}"
        for pk in Attempt.objects.filter(questionnaire_id__in=quiz_ids).values_list(
            "id", flat=True
        )
    ]
    if not sources:
        return
    victims = list(
        Measurement.objects.filter(source__in=sources).values_list("user_id", "cut")
    )
    Measurement.objects.filter(source__in=sources).delete()

    # Ular bekor qilgan haqiqiy o'lchovni qaytaramiz.
    for user_id, cut in set(victims):
        rows = Measurement.objects.filter(user_id=user_id, cut=cut)
        if rows.filter(is_void=False).exists():
            continue
        latest = rows.order_by("-created_at").first()
        if latest is not None:
            latest.is_void = False
            latest.void_reason = ""
            latest.save(update_fields=["is_void", "void_reason"])


def backwards(apps, schema_editor):
    Questionnaire = apps.get_model("diagnostics", "Questionnaire")
    Questionnaire.objects.filter(kind="QUIZ").update(kind="TEST")


class Migration(migrations.Migration):

    dependencies = [
        ("diagnostics", "0002_alter_questionnaire_kind"),
        ("content", "0001_initial"),
    ]

    operations = [migrations.RunPython(forwards, backwards)]
