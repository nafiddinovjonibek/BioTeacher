"""
Smoke-testlar: har bir sahifa har bir rol uchun xatosiz render bo'lishi.

Bu testlar shablon xatolarini, noto'g'ri URL nomlarini va kontekst
yetishmovchiligini erta tutadi.
"""

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from accounts.models import Enrollment, StudyGroup
from assignments.models import Assignment, Submission
from content.models import Lesson
from core.enums import Cut, Module, Role, StudyArm
from diagnostics.models import Measurement, Questionnaire
from goals.models import Goal, GoalTask
from reflection.models import ReflectionEntry

User = get_user_model()


class PublicPagesTests(TestCase):
    def test_landing(self):
        self.assertEqual(self.client.get(reverse("home:landing")).status_code, 200)

    def test_about(self):
        self.assertEqual(self.client.get(reverse("home:about")).status_code, 200)

    def test_login_page(self):
        self.assertEqual(self.client.get(reverse("accounts:login")).status_code, 200)

    def test_register_page(self):
        self.assertEqual(self.client.get(reverse("accounts:register")).status_code, 200)

    def test_password_reset_page(self):
        self.assertEqual(self.client.get(reverse("accounts:password_reset")).status_code, 200)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("home:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response["Location"])

    def test_404_page(self):
        self.assertEqual(self.client.get("/bunday-sahifa-yoq/").status_code, 404)


class SeededPagesTests(TestCase):
    """Kontent yuklangan holatda barcha rol sahifalarini tekshiradi."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)

        cls.mentor = User.objects.create_user("mentor-smoke@test.uz", "parol12345")
        cls.mentor.profile.role = Role.TEACHER
        cls.mentor.profile.save()

        cls.group = StudyGroup.objects.create(
            name="Smoke guruh", teacher=cls.mentor, study_arm=StudyArm.EXPERIMENTAL
        )

        cls.student = User.objects.create_user("talaba-smoke@test.uz", "parol12345")
        cls.student.first_name, cls.student.last_name = "Aziza", "Karimova"
        cls.student.save()
        cls.student.profile.group = cls.group
        cls.student.profile.onboarding_done = True
        cls.student.profile.save()
        Enrollment.objects.create(student=cls.student, group=cls.group)

        cls.researcher = User.objects.create_user("tadqiqot-smoke@test.uz", "parol12345")
        cls.researcher.profile.role = Role.RESEARCHER
        cls.researcher.profile.save()

        # Talaba uchun ma'lumot: o'lchov, maqsad, refleksiya, yuborilgan ish.
        Measurement.objects.create(user=cls.student, cut=Cut.INITIAL,
                                   mot=50, cog=55, act=45, ref=40, cre=60)
        Measurement.objects.create(user=cls.student, cut=Cut.FINAL,
                                   mot=70, cog=75, act=65, ref=68, cre=72)

        goal = Goal.objects.create(
            user=cls.student, title="Muammoli ta'limni o'rganish",
            deadline="2026-12-31", why="Zarur", expected_result="2 ta fragment",
        )
        GoalTask.objects.create(goal=goal, title="Metodni o'rganish", week=1)
        cls.goal = goal

        cls.assignment = Assignment.objects.first()
        cls.submission = Submission.objects.create(
            assignment=cls.assignment, student=cls.student,
            status=Submission.Status.SUBMITTED, payload={"hypothesis": "Taxminim"},
        )
        cls.reflection = ReflectionEntry.objects.create(
            user=cls.student, kind=ReflectionEntry.Kind.TASK,
            submission=cls.submission,
            q1="Bugun fotosintez bosqichlarini aniq farqlashni o'rgandim, chunki sxemani o'zim tuzdim.",
            q2="Tajriba rejasida nazorat namunasini ko'zda tutdim va bu natijani ishonchli qildi.",
            q3="Miqdoriy o'lchashni yaxshilashim kerak, hozircha sifatiy tavsif bilan cheklandim.",
            q4="Keyingi safar o'lchov jadvalini oldindan tayyorlayman va tarozida o'lchataman.",
            quality_score=78.0, quality_detail={"completeness": 90, "hints": []},
        )
        cls.lesson = Lesson.objects.first()
        cls.questionnaire = Questionnaire.objects.filter(cut=Cut.INITIAL).first()

    def assert_ok(self, url, msg=""):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, f"{url} → {response.status_code} {msg}")
        return response

    # ------------------------------------------------------------ talaba

    def test_student_pages(self):
        self.client.force_login(self.student)
        for url in [
            reverse("home:dashboard"),
            reverse("home:cabinet"),
            reverse("accounts:profile_edit"),
            reverse("accounts:join_group"),
            reverse("accounts:consent"),
            reverse("diagnostics:index"),
            reverse("goals:list"),
            reverse("goals:create"),
            reverse("goals:detail", args=[self.goal.pk]),
            reverse("goals:edit", args=[self.goal.pk]),
            reverse("goals:reflect", args=[self.goal.pk]),
            reverse("content:index"),
            reverse("content:topic", args=[self.lesson.topic.section.slug, self.lesson.topic.slug]),
            reverse("content:lesson", args=[self.lesson.topic.section.slug,
                                            self.lesson.topic.slug, self.lesson.slug]),
            reverse("content:lesson_quiz", args=[self.lesson.pk]),
            reverse("assignments:module", args=[Module.LAB]),
            reverse("assignments:module", args=[Module.TEACHER]),
            reverse("assignments:module", args=[Module.DIGITAL]),
            reverse("assignments:module", args=[Module.CREATIVE]),
            reverse("assignments:detail", args=[self.assignment.slug]),
            reverse("assignments:submission", args=[self.submission.pk]),
            reverse("assignments:self_assess", args=[self.submission.pk]),
            reverse("assignments:gallery"),
            reverse("assignments:competency"),
            reverse("reflection:journal"),
            reverse("reflection:create_free"),
            reverse("reflection:detail", args=[self.reflection.pk]),
            reverse("progress:monitoring"),
            reverse("gamification:achievements"),
            reverse("notifications:inbox"),
            reverse("notifications:settings"),
        ]:
            with self.subTest(url=url):
                self.assert_ok(url)

    def test_student_can_start_and_take_diagnostic(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("diagnostics:start", args=[self.questionnaire.slug]))
        self.assertEqual(response.status_code, 302)
        self.assert_ok(response["Location"])

    def test_old_profile_url_redirects_to_cabinet(self):
        """Eski /hisob/profil/ manzili kabinetga ko'chdi."""
        self.client.force_login(self.student)
        response = self.client.get(reverse("accounts:profile"))
        self.assertRedirects(response, reverse("home:cabinet"))

    def test_student_pdf_report(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("progress:report_pdf"))
        self.assertEqual(response.status_code, 200)

    # ----------------------------------------------------------- onboarding

    def test_new_student_is_blocked_until_diagnostic(self):
        """FR-06 — onboarding tugamaguncha boshqa sahifalar bloklanadi."""
        fresh = User.objects.create_user("yangi@test.uz", "parol12345")
        self.client.force_login(fresh)
        response = self.client.get(reverse("content:index"))
        self.assertRedirects(response, reverse("accounts:onboarding"))

    def test_onboarding_page_renders(self):
        fresh = User.objects.create_user("yangi2@test.uz", "parol12345")
        self.client.force_login(fresh)
        self.assert_ok(reverse("accounts:onboarding"))

    # ------------------------------------------------------------ mentor

    def test_teacher_pages(self):
        self.client.force_login(self.mentor)
        for url in [
            reverse("teacher:groups"),
            reverse("teacher:group_create"),
            reverse("teacher:group_detail", args=[self.group.pk]),
            reverse("teacher:analytics", args=[self.group.pk]),
            reverse("teacher:announce", args=[self.group.pk]),
            reverse("assignments:queue"),
            reverse("assignments:grade", args=[self.submission.pk]),
            reverse("progress:student", args=[self.student.pk]),
            reverse("goals:review", args=[self.goal.pk]),
            reverse("goals:detail", args=[self.goal.pk]),
        ]:
            with self.subTest(url=url):
                self.assert_ok(url)

    def test_teacher_dashboard_redirects_to_cabinet(self):
        self.client.force_login(self.mentor)
        self.assertRedirects(reverse("home:dashboard") and
                             self.client.get(reverse("home:dashboard")),
                             reverse("teacher:groups"))

    # --------------------------------------------------------- tadqiqotchi

    def test_researcher_pages(self):
        self.client.force_login(self.researcher)
        for url in [
            reverse("research:dashboard"),
            reverse("research:statistics"),
            reverse("research:export"),
            reverse("research:set_arm", args=[self.group.pk]),
        ]:
            with self.subTest(url=url):
                self.assert_ok(url)

    def test_researcher_dashboard_redirect(self):
        self.client.force_login(self.researcher)
        self.assertRedirects(self.client.get(reverse("home:dashboard")),
                             reverse("research:dashboard"))


class TemplateHygieneTests(TestCase):
    """Shablonlardagi tipik xatolarni tutadi."""

    def test_no_multiline_django_comments(self):
        """
        Django'da `{# ... #}` FAQAT bir qatorlik izoh.

        Ko'p qatorli bo'lsa Django uni izoh deb tanimaydi va matn sifatida
        sahifaga chiqaradi — bu ikki marta sodir bo'lgan. Ko'p qatorli izoh
        uchun `{% comment %}` ishlatiladi.
        """
        import re
        from pathlib import Path

        from django.conf import settings

        newline = chr(10)
        offenders = []
        for template_dir in settings.TEMPLATES[0]["DIRS"]:
            for path in Path(template_dir).rglob("*.html"):
                text = path.read_text(encoding="utf-8")
                for match in re.finditer(r"\{#(.*?)#\}", text, re.S):
                    if newline in match.group(1):
                        offenders.append(f"{path.name}: {match.group(0)[:60]}")
        self.assertEqual(
            offenders, [],
            "Ko'p qatorli {# #} izohlar sahifaga matn bo'lib chiqadi; "
            "{% comment %} ishlating. Topilganlar: " + "; ".join(offenders),
        )



class SeedIntegrityTests(TestCase):
    """Seed kontenti TZ 10-bo'limdagi tuzilmaga mos bo'lishi."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)

    def test_every_question_has_component_and_bloom(self):
        from diagnostics.models import Question

        self.assertFalse(Question.objects.filter(component="").exists())
        self.assertFalse(Question.objects.filter(bloom_level__isnull=True).exists())

    def test_every_test_question_has_exactly_one_correct_choice(self):
        from diagnostics.models import Question

        for question in Question.objects.filter(questionnaire__kind="TEST"):
            correct = question.choices.filter(is_correct=True).count()
            self.assertEqual(correct, 1, f"'{question.text[:40]}' → {correct} ta to'g'ri javob")

    def test_likert_covers_all_five_components(self):
        from diagnostics.models import Question

        components = set(
            Question.objects.filter(questionnaire__kind="LIKERT")
            .values_list("component", flat=True)
        )
        self.assertEqual(components, {"MOT", "COG", "ACT", "REF", "CRE"})

    def test_every_assignment_has_rubric_with_criteria(self):
        for assignment in Assignment.objects.all():
            self.assertTrue(
                assignment.rubric.criteria.exists(),
                f"'{assignment.title}' rubrikasida mezon yo'q",
            )

    def test_all_five_modules_have_assignments(self):
        modules = set(Assignment.objects.values_list("module", flat=True))
        for module in [Module.LAB, Module.TEACHER, Module.DIGITAL, Module.CREATIVE]:
            self.assertIn(module, modules)

    def test_badges_have_rules(self):
        from gamification.models import Badge

        for badge in Badge.objects.all():
            self.assertTrue(badge.rules.exists(), f"'{badge.title}' qoidasiz")

    def test_reflection_prompts_cover_four_slots(self):
        from reflection.models import ReflectionPrompt

        slots = set(ReflectionPrompt.objects.values_list("slot", flat=True))
        self.assertEqual(slots, {1, 2, 3, 4})

    def test_seed_is_idempotent(self):
        from diagnostics.models import Question

        before = (Assignment.objects.count(), Question.objects.count(), Lesson.objects.count())
        call_command("seed_demo", verbosity=0)
        after = (Assignment.objects.count(), Question.objects.count(), Lesson.objects.count())
        self.assertEqual(before, after)
