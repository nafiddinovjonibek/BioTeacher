"""Nishonlar tizimi testlari (FR-49..FR-52, SR-07)."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from assignments.models import Assignment, Criterion, Rubric, Submission
from core.enums import BloomLevel, Component, Cut, Module
from diagnostics.models import Measurement
from progress.models import Streak
from reflection.models import ReflectionEntry

from .models import Badge, BadgeRule, UserBadge
from .services import badge_board, evaluate_badges, metric_sdi_growth

User = get_user_model()


class BadgeAwardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("nishon@test.uz", "parol12345")
        self.badge = Badge.objects.create(
            code="tadqiqotchi", title="Yosh tadqiqotchi", emoji="🔬",
            how_to_earn="Laboratoriyada 3 ta ish",
        )
        BadgeRule.objects.create(
            badge=self.badge, metric=BadgeRule.Metric.LAB_SUBMISSIONS, threshold=3
        )

        rubric = Rubric.objects.create(title="R", slug="r-badge")
        Criterion.objects.create(rubric=rubric, name="M", max_score=4)
        self.assignments = [
            Assignment.objects.create(
                module=Module.LAB, kind=Assignment.Kind.LAB4, title=f"Lab {i}",
                slug=f"lab-{i}", body="x", component=Component.COG,
                bloom_level=BloomLevel.APPLY, rubric=rubric,
            )
            for i in range(4)
        ]

    def _submit(self, count):
        for assignment in self.assignments[:count]:
            Submission.objects.create(
                assignment=assignment, student=self.user,
                status=Submission.Status.SUBMITTED, submitted_at=timezone.now(),
            )

    def test_badge_not_awarded_below_threshold(self):
        self._submit(2)
        evaluate_badges(self.user)
        self.assertFalse(UserBadge.objects.filter(user=self.user).exists())

    def test_badge_awarded_at_threshold(self):
        self._submit(3)
        awarded = evaluate_badges(self.user)
        self.assertEqual(awarded, [self.badge])
        self.assertTrue(UserBadge.objects.filter(user=self.user, badge=self.badge).exists())

    def test_badge_is_not_awarded_twice(self):
        self._submit(4)
        evaluate_badges(self.user)
        evaluate_badges(self.user)
        self.assertEqual(UserBadge.objects.filter(user=self.user).count(), 1)

    def test_award_creates_notification(self):
        from notifications.models import Notification, NotificationType

        self._submit(3)
        evaluate_badges(self.user)
        self.assertTrue(
            Notification.objects.filter(user=self.user, kind=NotificationType.BADGE).exists()
        )

    def test_multiple_rules_must_all_be_satisfied(self):
        BadgeRule.objects.create(
            badge=self.badge, metric=BadgeRule.Metric.STREAK, threshold=5
        )
        self._submit(4)
        evaluate_badges(self.user)
        self.assertFalse(UserBadge.objects.filter(user=self.user).exists())

        Streak.objects.create(user=self.user, current=5, longest=5)
        evaluate_badges(self.user)
        self.assertTrue(UserBadge.objects.filter(user=self.user).exists())


class BadgeBoardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("taxta@test.uz", "parol12345")
        self.user.profile.onboarding_done = True
        self.user.profile.save()
        badge = Badge.objects.create(code="muntazam", title="Muntazam", emoji="🏅",
                                     how_to_earn="10 kun ketma-ket")
        BadgeRule.objects.create(badge=badge, metric=BadgeRule.Metric.STREAK, threshold=10)

    def test_progress_is_reported_for_unearned_badge(self):
        Streak.objects.create(user=self.user, current=5, longest=5)
        row = badge_board(self.user)[0]
        self.assertIsNone(row["earned"])
        self.assertEqual(row["progress"], 50)

    def test_progress_is_capped_at_hundred(self):
        Streak.objects.create(user=self.user, current=50, longest=50)
        row = badge_board(self.user)[0]
        self.assertEqual(row["progress"], 100)

    def test_achievements_page_has_no_leaderboard(self):
        """SR-07 / FR-51 — ochiq reyting jadvali bo'lmasligi shart."""
        other = User.objects.create_user("boshqa-talaba@test.uz", "parol12345")
        other.first_name = "Begona"
        other.save()

        self.client.force_login(self.user)
        response = self.client.get(reverse("gamification:achievements"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Begona")
        self.assertNotContains(response, other.email)


class GrowthMetricTests(TestCase):
    """SR-07 — o'sish faqat o'z oldingi natijasiga nisbatan o'lchanadi."""

    def setUp(self):
        self.user = User.objects.create_user("osish@test.uz", "parol12345")

    def test_growth_between_measurements(self):
        Measurement.objects.create(user=self.user, cut=Cut.INITIAL,
                                   mot=40, cog=40, act=40, ref=40, cre=40)
        Measurement.objects.create(user=self.user, cut=Cut.FINAL,
                                   mot=70, cog=70, act=70, ref=70, cre=70)
        self.assertAlmostEqual(metric_sdi_growth(self.user), 30.0, places=1)

    def test_growth_is_zero_without_history(self):
        self.assertEqual(metric_sdi_growth(self.user), 0)

    def test_growth_ignores_other_users(self):
        other = User.objects.create_user("boshqa-osish@test.uz", "parol12345")
        Measurement.objects.create(user=other, cut=Cut.INITIAL,
                                   mot=10, cog=10, act=10, ref=10, cre=10)
        Measurement.objects.create(user=other, cut=Cut.FINAL,
                                   mot=90, cog=90, act=90, ref=90, cre=90)
        self.assertEqual(metric_sdi_growth(self.user), 0)


class ReflectionBadgeTests(TestCase):
    def test_reflection_badge_uses_entry_count(self):
        user = User.objects.create_user("refnishon@test.uz", "parol12345")
        badge = Badge.objects.create(code="refleksiv", title="Refleksiv", emoji="🔍",
                                     how_to_earn="2 ta refleksiya")
        BadgeRule.objects.create(badge=badge, metric=BadgeRule.Metric.REFLECTIONS, threshold=2)

        for index in range(2):
            ReflectionEntry.objects.create(
                user=user, kind=ReflectionEntry.Kind.FREE,
                free_text=f"Yozuv {index}", quality_score=70,
            )
        evaluate_badges(user)
        self.assertTrue(UserBadge.objects.filter(user=user, badge=badge).exists())
