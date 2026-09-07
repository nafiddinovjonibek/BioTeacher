"""
Rivojlanish yadrosi va TO'LIQ SIKL integratsiya testi.

TZ 12-bo'limdagi 3-mezon: talaba topshiriq bajaradi → o'zini baholaydi →
mentor baholaydi → refleksiya yozadi, va bularning hammasi ko'rsatkichga ta'sir qiladi.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from accounts.models import Enrollment, StudyGroup
from assignments.models import Assignment, Criterion, Rubric, Score, Submission
from assignments.services import apply_scores, finalize_submission
from core.enums import BloomLevel, Component, Cut, Module, Role
from diagnostics.models import Measurement, ScoringWeights
from reflection.models import ReflectionEntry
from reflection.services import save_with_score

from .models import ActivityLog, ComponentScore, ProgressSnapshot, Streak
from .services import (
    blend,
    current_scores,
    current_sdi,
    daily_task_for,
    dynamics_summary,
    log_activity,
    recompute,
    recommended_assignments,
    touch_streak,
    weakest_components,
)

User = get_user_model()


class BlendTests(TestCase):
    def test_both_sources_are_weighted(self):
        value, diagnostic, practice = blend(100, 0)
        self.assertEqual(diagnostic, 100)
        self.assertEqual(practice, 0)
        self.assertAlmostEqual(value, 40.0, places=1)  # 100*0.4 + 0*0.6

    def test_only_diagnostic_takes_full_weight(self):
        self.assertEqual(blend(80, None)[0], 80.0)

    def test_only_practice_takes_full_weight(self):
        self.assertEqual(blend(None, 80)[0], 80.0)

    def test_no_data_returns_none(self):
        self.assertEqual(blend(None, None), (None, None, None))


class StreakTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("streak@test.uz", "parol12345")

    def test_first_activity_starts_streak(self):
        streak = touch_streak(self.user)
        self.assertEqual(streak.current, 1)
        self.assertEqual(streak.longest, 1)

    def test_same_day_does_not_increment(self):
        touch_streak(self.user)
        streak = touch_streak(self.user)
        self.assertEqual(streak.current, 1)

    def test_consecutive_day_increments(self):
        streak = Streak.objects.create(
            user=self.user, current=3, longest=3,
            last_active_date=timezone.localdate() - timedelta(days=1),
        )
        streak = touch_streak(self.user)
        self.assertEqual(streak.current, 4)
        self.assertEqual(streak.longest, 4)

    def test_gap_resets_streak_but_keeps_longest(self):
        Streak.objects.create(
            user=self.user, current=7, longest=7,
            last_active_date=timezone.localdate() - timedelta(days=5),
        )
        streak = touch_streak(self.user)
        self.assertEqual(streak.current, 1)
        self.assertEqual(streak.longest, 7)


class DailyTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("kunlik@test.uz", "parol12345")

    def test_same_task_returned_for_same_day(self):
        first = daily_task_for(self.user)
        second = daily_task_for(self.user)
        self.assertEqual(first.pk, second.pk)

    def test_task_has_component_and_text(self):
        task = daily_task_for(self.user)
        self.assertIn(task.component, Component.values)
        self.assertTrue(task.description)


class TrajectoryTests(TestCase):
    """FR-12 / FR-67 — traektoriya eng zaif komponentga yo'naltiriladi."""

    def setUp(self):
        self.user = User.objects.create_user("traektoriya@test.uz", "parol12345")
        rubric = Rubric.objects.create(title="R", slug="r")
        Criterion.objects.create(rubric=rubric, name="M", max_score=4)
        for index, component in enumerate(Component.values):
            Assignment.objects.create(
                module=Module.LAB, kind=Assignment.Kind.LAB4,
                title=f"Topshiriq {component}", slug=f"topshiriq-{index}",
                body="matn", component=component, bloom_level=BloomLevel.APPLY, rubric=rubric,
            )
        for component, value in [("MOT", 90), ("COG", 85), ("ACT", 30), ("REF", 20), ("CRE", 70)]:
            ComponentScore.objects.create(user=self.user, component=component, value=value)

    def test_weakest_components_are_detected(self):
        self.assertEqual(set(weakest_components(self.user)), {"REF", "ACT"})

    def test_recommendations_target_weak_components(self):
        recommended = recommended_assignments(self.user, limit=2)
        self.assertTrue(all(a.component in {"REF", "ACT"} for a in recommended))

    def test_completed_assignments_are_excluded(self):
        weak = Assignment.objects.get(component="REF")
        Submission.objects.create(assignment=weak, student=self.user)
        recommended = recommended_assignments(self.user, limit=5)
        self.assertNotIn(weak, recommended)


class FullCycleTests(TestCase):
    """
    TZ 12-bo'lim, 3-4 mezon — to'liq sikl integratsiya testi.

    Diagnostika → topshiriq → o'z bahosi → mentor bahosi → refleksiya → monitoring.
    """

    def setUp(self):
        ScoringWeights.objects.create(name="Standart", is_active=True)

        self.mentor = User.objects.create_user("mentor-sikl@test.uz", "parol12345")
        self.mentor.profile.role = Role.TEACHER
        self.mentor.profile.save()
        self.group = StudyGroup.objects.create(name="Sikl guruh", teacher=self.mentor)

        self.student = User.objects.create_user("talaba-sikl@test.uz", "parol12345")
        self.student.profile.group = self.group
        self.student.profile.save()
        Enrollment.objects.create(student=self.student, group=self.group)

        self.rubric = Rubric.objects.create(title="Rubrika", slug="rubrika-sikl")
        self.criterion = Criterion.objects.create(
            rubric=self.rubric, name="Asoslilik", max_score=4, weight=1.0
        )
        self.assignment = Assignment.objects.create(
            module=Module.LAB, kind=Assignment.Kind.LAB4, title="Sikl topshirig'i",
            slug="sikl-topshirigi", body="matn", component=Component.ACT,
            bloom_level=BloomLevel.APPLY, rubric=self.rubric,
        )

    def test_full_cycle_moves_the_needle(self):
        # 1. Boshlang'ich diagnostika o'lchovi
        Measurement.objects.create(
            user=self.student, cut=Cut.INITIAL, mot=40, cog=40, act=40, ref=40, cre=40
        )
        for component in Component.values:
            ComponentScore.objects.create(user=self.student, component=component, value=40)
        initial_sdi = current_sdi(self.student)
        self.assertAlmostEqual(initial_sdi, 40.0, places=1)

        # 2. Topshiriq bajarish va o'zini baholash
        submission = Submission.objects.create(
            assignment=self.assignment, student=self.student,
            payload={"hypothesis": "taxmin", "plan": "reja"},
        )
        apply_scores(submission, Score.Scorer.SELF, {self.criterion.id: 4}, author=self.student)
        finalize_submission(submission)
        submission.refresh_from_db()
        self.assertEqual(submission.status, Submission.Status.SUBMITTED)
        self.assertEqual(submission.self_percent, 100.0)

        # 3. Mentor bahosi
        apply_scores(submission, Score.Scorer.MENTOR, {self.criterion.id: 3}, author=self.mentor)
        recompute(self.student)
        submission.refresh_from_db()
        self.assertEqual(submission.status, Submission.Status.GRADED)
        self.assertEqual(submission.mentor_percent, 75.0)
        self.assertEqual(submission.assessment_gap, 25.0)

        # ACT ko'rsatkichi mentor bahosini hisobga oldi (diagnostika 40, amaliyot 75)
        act = ComponentScore.objects.get(user=self.student, component=Component.ACT)
        self.assertGreater(act.value, 40)

        # 4. Refleksiya REF ko'rsatkichini oshiradi
        ref_before = ComponentScore.objects.get(user=self.student, component=Component.REF).value
        entry = ReflectionEntry.objects.create(
            user=self.student, kind=ReflectionEntry.Kind.TASK, submission=submission,
            q1="Bugun tajriba rejasida nazorat namunasi nima uchun kerakligini tushundim, "
               "chunki usiz natijani boshqa omil bilan chalkashtirish mumkin edi.",
            q2="Taxminimni biologik qonuniyatga tayanib yozdim va bu yaxshi chiqdi.",
            q3="Natijani miqdoriy o'lchashni rivojlantirishim kerak, hozircha sifatiy tavsif berdim.",
            q4="Keyingi safar o'lchov jadvalini oldindan tayyorlayman va massani tarozida o'lchayman.",
        )
        save_with_score(entry)
        entry.refresh_from_db()
        self.assertIsNotNone(entry.quality_score)
        ref_after = ComponentScore.objects.get(user=self.student, component=Component.REF).value
        self.assertNotEqual(ref_before, ref_after)

        # 5. Monitoring: SDI o'zgardi va kesma yozildi
        final_sdi = current_sdi(self.student)
        self.assertGreater(final_sdi, initial_sdi)
        self.assertTrue(ProgressSnapshot.objects.filter(user=self.student).exists())

        # 6. Faollik jurnali to'ldi
        actions = set(
            ActivityLog.objects.filter(user=self.student).values_list("action", flat=True)
        )
        self.assertIn(ActivityLog.Action.SUBMISSION, actions)
        self.assertIn(ActivityLog.Action.REFLECTION, actions)

    def test_dynamics_summary_reports_growth(self):
        Measurement.objects.create(
            user=self.student, cut=Cut.INITIAL, mot=40, cog=40, act=40, ref=40, cre=40
        )
        Measurement.objects.create(
            user=self.student, cut=Cut.FINAL, mot=70, cog=70, act=70, ref=70, cre=70
        )
        summary = dynamics_summary(self.student)
        self.assertIsNotNone(summary)
        self.assertIn("o'sdi", summary)

    def test_snapshot_is_one_per_day(self):
        recompute(self.student)
        recompute(self.student)
        self.assertEqual(ProgressSnapshot.objects.filter(user=self.student).count(), 1)
