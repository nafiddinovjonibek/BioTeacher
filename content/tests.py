"""BioBilim moduli va kontent import buyrug'i testlari (FR-20, FR-21, FR-68)."""

import tempfile
from io import StringIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import TestCase

from assignments.models import Assignment, Criterion, Rubric
from diagnostics.models import Question, Questionnaire

from .models import Lesson, LessonProgress, Section, Topic

User = get_user_model()


class LessonProgressTests(TestCase):
    """FR-20 — o'zlashtirish chegarasi."""

    def setUp(self):
        self.user = User.objects.create_user("dars@test.uz", "parol12345")
        section = Section.objects.create(title="Bo'lim", slug="bolim")
        topic = Topic.objects.create(section=section, title="Mavzu", slug="mavzu")
        self.lesson = Lesson.objects.create(
            topic=topic, title="Dars", slug="dars", pass_threshold=70
        )

    def test_score_above_threshold_passes(self):
        progress = LessonProgress.objects.create(user=self.user, lesson=self.lesson)
        self.assertEqual(progress.mark(85), LessonProgress.Status.PASSED)
        self.assertIsNotNone(progress.completed_at)

    def test_score_below_threshold_fails(self):
        """FR-21 — chegaradan past natija qayta ko'rishga yo'naltiradi."""
        progress = LessonProgress.objects.create(user=self.user, lesson=self.lesson)
        self.assertEqual(progress.mark(65), LessonProgress.Status.FAILED)
        self.assertIsNone(progress.completed_at)

    def test_exact_threshold_passes(self):
        progress = LessonProgress.objects.create(user=self.user, lesson=self.lesson)
        self.assertEqual(progress.mark(70), LessonProgress.Status.PASSED)

    def test_attempts_are_counted(self):
        progress = LessonProgress.objects.create(user=self.user, lesson=self.lesson)
        progress.mark(50)
        progress.mark(80)
        self.assertEqual(progress.attempts, 2)
        self.assertEqual(progress.status, LessonProgress.Status.PASSED)

    def test_lesson_score_feeds_cog_component(self):
        from progress.models import ComponentScore
        from progress.services import recompute

        progress = LessonProgress.objects.create(user=self.user, lesson=self.lesson)
        progress.mark(90)
        recompute(self.user)
        self.assertEqual(
            ComponentScore.objects.get(user=self.user, component="COG").value, 90.0
        )


class ImportContentTests(TestCase):
    """FR-68 — metodist CSV/XLSX orqali kontent yuklaydi."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.rubric = Rubric.objects.create(title="Rubrika", slug="import-rubrika")
        Criterion.objects.create(rubric=self.rubric, name="Mezon", max_score=4)
        self.questionnaire = Questionnaire.objects.create(
            title="Import testi", slug="import-test", kind=Questionnaire.Kind.TEST
        )

    def _run(self, *args):
        out = StringIO()
        call_command("import_content", *args, stdout=out)
        return out.getvalue()

    def _csv(self, name, header, *rows):
        path = self.tmp / name
        lines = [";".join(header)] + [";".join(row) for row in rows]
        path.write_text("\n".join(lines), encoding="utf-8-sig")
        return path

    # --- namuna fayl ---

    def test_template_csv_is_created(self):
        out = self.tmp / "namuna.csv"
        self._run("--template", "assignments", "--out", str(out))
        self.assertTrue(out.exists())
        self.assertIn("rubric_slug", out.read_text(encoding="utf-8-sig"))

    def test_template_xlsx_is_created(self):
        out = self.tmp / "namuna.xlsx"
        self._run("--template", "questions", "--out", str(out))
        self.assertTrue(out.exists())
        self.assertGreater(out.stat().st_size, 0)

    # --- savollar ---

    def test_questions_are_imported_with_choices(self):
        header = ["questionnaire_slug", "text", "component", "bloom", "reverse",
                  "variant_1", "variant_2", "variant_3", "variant_4", "correct", "explanation"]
        path = self._csv(
            "savollar.csv", header,
            ["import-test", "Mitoxondriya vazifasi nima?", "COG", "2", "",
             "ATF sintezi", "Oqsil sintezi", "Fotosintez", "Tashish", "1", "Nafas olish organoidi"],
        )
        self._run("--type", "questions", "--file", str(path))

        question = Question.objects.get(text="Mitoxondriya vazifasi nima?")
        self.assertEqual(question.component, "COG")
        self.assertEqual(question.bloom_level, 2)
        self.assertEqual(question.choices.count(), 4)
        self.assertEqual(question.correct_choice().text, "ATF sintezi")

    def test_likert_question_without_choices(self):
        header = ["questionnaire_slug", "text", "component", "bloom", "reverse",
                  "variant_1", "variant_2", "variant_3", "variant_4", "correct", "explanation"]
        path = self._csv(
            "likert.csv", header,
            ["import-test", "Men muntazam o'qiyman", "MOT", "1", "1", "", "", "", "", "", ""],
        )
        self._run("--type", "questions", "--file", str(path))
        question = Question.objects.get(text="Men muntazam o'qiyman")
        self.assertTrue(question.reverse_scored)
        self.assertEqual(question.choices.count(), 0)

    def test_invalid_component_is_reported(self):
        header = ["questionnaire_slug", "text", "component", "bloom", "reverse",
                  "variant_1", "variant_2", "variant_3", "variant_4", "correct", "explanation"]
        path = self._csv("xato.csv", header,
                         ["import-test", "Savol", "XXX", "1", "", "", "", "", "", "", ""])
        output = self._run("--type", "questions", "--file", str(path))
        self.assertIn("noma'lum komponent", output)
        self.assertEqual(Question.objects.count(), 0)

    def test_missing_questionnaire_is_reported(self):
        header = ["questionnaire_slug", "text", "component", "bloom", "reverse",
                  "variant_1", "variant_2", "variant_3", "variant_4", "correct", "explanation"]
        path = self._csv("yoq.csv", header,
                         ["mavjud-emas", "Savol", "COG", "1", "", "", "", "", "", "", ""])
        output = self._run("--type", "questions", "--file", str(path))
        self.assertIn("topilmadi", output)

    # --- topshiriqlar ---

    def test_assignments_are_imported(self):
        header = ["slug", "module", "kind", "title", "component", "bloom", "difficulty",
                  "minutes", "rubric_slug", "context", "body", "reference"]
        path = self._csv(
            "topshiriq.csv", header,
            ["import-lab", "LAB", "LAB4", "Import topshirig'i", "COG", "4", "3", "30",
             "import-rubrika", "Vaziyat", "Topshiriq matni", "Etalon"],
        )
        self._run("--type", "assignments", "--file", str(path))

        assignment = Assignment.objects.get(slug="import-lab")
        self.assertEqual(assignment.module, "LAB")
        self.assertEqual(assignment.bloom_level, 4)
        self.assertEqual(assignment.rubric, self.rubric)

    def test_assignment_with_unknown_rubric_is_reported(self):
        header = ["slug", "module", "kind", "title", "component", "bloom", "difficulty",
                  "minutes", "rubric_slug", "context", "body", "reference"]
        path = self._csv(
            "xato-rubrika.csv", header,
            ["x", "LAB", "LAB4", "T", "COG", "4", "3", "30", "yoq", "", "matn", ""],
        )
        output = self._run("--type", "assignments", "--file", str(path))
        self.assertIn("rubrikasi topilmadi", output)

    # --- darslar ---

    def test_lessons_create_missing_section_and_topic(self):
        header = ["section_title", "section_slug", "topic_title", "topic_slug",
                  "lesson_title", "lesson_slug", "duration", "body"]
        path = self._csv(
            "darslar.csv", header,
            ["Yangi bo'lim", "yangi-bolim", "Yangi mavzu", "yangi-mavzu",
             "Yangi dars", "yangi-dars", "25", "Dars matni"],
        )
        self._run("--type", "lessons", "--file", str(path))

        self.assertTrue(Section.objects.filter(slug="yangi-bolim").exists())
        self.assertTrue(Topic.objects.filter(slug="yangi-mavzu").exists())
        lesson = Lesson.objects.get(slug="yangi-dars")
        self.assertEqual(lesson.duration_minutes, 25)

    # --- umumiy ---

    def test_dry_run_writes_nothing(self):
        header = ["slug", "module", "kind", "title", "component", "bloom", "difficulty",
                  "minutes", "rubric_slug", "context", "body", "reference"]
        path = self._csv(
            "dry.csv", header,
            ["dry-lab", "LAB", "LAB4", "T", "COG", "4", "3", "30",
             "import-rubrika", "", "matn", ""],
        )
        self._run("--type", "assignments", "--file", str(path), "--dry-run")
        self.assertFalse(Assignment.objects.filter(slug="dry-lab").exists())

    def test_import_is_idempotent(self):
        header = ["slug", "module", "kind", "title", "component", "bloom", "difficulty",
                  "minutes", "rubric_slug", "context", "body", "reference"]
        path = self._csv(
            "takror.csv", header,
            ["takror", "LAB", "LAB4", "T", "COG", "4", "3", "30",
             "import-rubrika", "", "matn", ""],
        )
        self._run("--type", "assignments", "--file", str(path))
        self._run("--type", "assignments", "--file", str(path))
        self.assertEqual(Assignment.objects.filter(slug="takror").count(), 1)

    def test_missing_column_raises(self):
        path = self._csv("kam.csv", ["slug", "title"], ["a", "b"])
        with self.assertRaises(CommandError) as ctx:
            self._run("--type", "assignments", "--file", str(path))
        self.assertIn("yetishmayapti", str(ctx.exception))

    def test_missing_file_raises(self):
        with self.assertRaises(CommandError):
            self._run("--type", "assignments", "--file", str(self.tmp / "yoq.csv"))
