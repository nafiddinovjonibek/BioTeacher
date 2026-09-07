"""Maqsad moduli testlari (FR-13..FR-17) va boshqaruv buyruqlari."""

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Enrollment, StudyGroup
from core.enums import Role
from reflection.models import ReflectionEntry

from .models import Goal, GoalTask

User = get_user_model()


def make_goal(user, **kwargs):
    defaults = {
        "title": "Muammoli ta'limni o'rganish",
        "deadline": timezone.localdate() + timezone.timedelta(days=28),
        "why": "Darsda o'quvchi faolligini oshirish uchun",
        "expected_result": "2 ta dars fragmenti",
    }
    defaults.update(kwargs)
    return Goal.objects.create(user=user, **defaults)


class GoalProgressTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("maqsad@test.uz", "parol12345")
        self.goal = make_goal(self.user)

    def test_progress_is_zero_without_tasks(self):
        self.assertEqual(self.goal.progress_percent(), 0)

    def test_progress_counts_completed_tasks(self):
        for index in range(4):
            GoalTask.objects.create(goal=self.goal, title=f"Vazifa {index}", week=index + 1)
        tasks = list(self.goal.tasks.all())
        tasks[0].toggle()
        tasks[1].toggle()
        self.assertEqual(self.goal.progress_percent(), 50)

    def test_toggle_is_reversible(self):
        task = GoalTask.objects.create(goal=self.goal, title="Vazifa")
        self.assertTrue(task.toggle())
        self.assertFalse(task.toggle())
        self.assertIsNone(task.done_at)

    def test_days_left_and_overdue(self):
        self.assertGreater(self.goal.days_left, 0)
        self.assertFalse(self.goal.is_overdue)

        past = make_goal(self.user, deadline=timezone.localdate() - timezone.timedelta(days=1))
        self.assertTrue(past.is_overdue)


class GoalClosingTests(TestCase):
    """FR-16 — yakuniy refleksiyasiz maqsad yopilmaydi."""

    def setUp(self):
        self.user = User.objects.create_user("yopish@test.uz", "parol12345")
        self.user.profile.onboarding_done = True
        self.user.profile.save()
        self.goal = make_goal(self.user)
        self.client.force_login(self.user)

    def test_cannot_close_without_reflection(self):
        self.assertFalse(self.goal.can_close())
        response = self.client.get(reverse("goals:close", args=[self.goal.pk]))
        self.assertRedirects(response, reverse("goals:reflect", args=[self.goal.pk]))
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.status, Goal.Status.ACTIVE)

    def test_closes_after_reflection(self):
        ReflectionEntry.objects.create(
            user=self.user, kind=ReflectionEntry.Kind.GOAL, goal=self.goal,
            q1="Muammoli ta'limni o'rgandim va uni 'Hujayra' mavzusiga qo'lladim.",
            q2="Fragmentni real vaqtga moslashtira oldim.",
            q3="Baholash mezonlarini aniqroq yozishim kerak.",
            q4="Keyingi safar mezonni o'quvchiga oldindan beraman.",
        )
        self.assertTrue(self.goal.can_close())
        self.client.get(reverse("goals:close", args=[self.goal.pk]))
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.status, Goal.Status.DONE)
        self.assertIsNotNone(self.goal.completed_at)


class GoalMentorReviewTests(TestCase):
    """FR-17 — mentor izoh qoldiradi va tasdiqlaydi."""

    def setUp(self):
        self.mentor = User.objects.create_user("mentor-maqsad@test.uz", "parol12345")
        self.mentor.profile.role = Role.TEACHER
        self.mentor.profile.save()
        self.group = StudyGroup.objects.create(name="M-guruh", teacher=self.mentor)

        self.student = User.objects.create_user("talaba-maqsad@test.uz", "parol12345")
        self.student.profile.group = self.group
        self.student.profile.onboarding_done = True
        self.student.profile.save()
        Enrollment.objects.create(student=self.student, group=self.group)

        self.goal = make_goal(self.student)

    def test_mentor_can_open_review(self):
        self.client.force_login(self.mentor)
        response = self.client.get(reverse("goals:review", args=[self.goal.pk]))
        self.assertEqual(response.status_code, 200)

    def test_mentor_approval_notifies_student(self):
        from notifications.models import Notification

        self.client.force_login(self.mentor)
        self.client.post(
            reverse("goals:review", args=[self.goal.pk]),
            {"comment": "Maqsad aniq va o'lchanadigan. Davom eting.", "approve": "1"},
        )
        self.goal.refresh_from_db()
        self.assertTrue(self.goal.mentor_approved)
        self.assertIsNotNone(self.goal.mentor_approved_at)
        self.assertTrue(
            Notification.objects.filter(user=self.student, kind="MENTOR_COMMENT").exists()
        )

    def test_approval_can_be_revoked(self):
        self.client.force_login(self.mentor)
        self.client.post(reverse("goals:review", args=[self.goal.pk]),
                         {"comment": "ok", "approve": "1"})
        self.client.post(reverse("goals:review", args=[self.goal.pk]),
                         {"comment": "Muddatni aniqlashtiring", "approve": "0"})
        self.goal.refresh_from_db()
        self.assertFalse(self.goal.mentor_approved)
        self.assertIsNone(self.goal.mentor_approved_at)

    def test_student_cannot_review_own_goal(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("goals:review", args=[self.goal.pk]))
        self.assertEqual(response.status_code, 403)

    def test_foreign_mentor_cannot_review(self):
        stranger = User.objects.create_user("begona-mentor@test.uz", "parol12345")
        stranger.profile.role = Role.TEACHER
        stranger.profile.save()
        self.client.force_login(stranger)
        response = self.client.get(reverse("goals:review", args=[self.goal.pk]))
        self.assertEqual(response.status_code, 403)


class ReminderCommandTests(TestCase):
    """FR-15 / FR-65 — eslatma va haftalik xulosa buyrug'i."""

    def setUp(self):
        self.user = User.objects.create_user("eslatma@test.uz", "parol12345")
        self.user.profile.onboarding_done = True
        self.user.profile.save()

    def _run(self, *args):
        out = StringIO()
        call_command("send_reminders", *args, stdout=out)
        return out.getvalue()

    def test_reminder_sent_for_near_deadline(self):
        from notifications.models import Notification

        make_goal(self.user, deadline=timezone.localdate() + timezone.timedelta(days=2))
        self._run()
        self.assertTrue(
            Notification.objects.filter(user=self.user, kind="DEADLINE").exists()
        )

    def test_no_reminder_for_far_deadline(self):
        from notifications.models import Notification

        make_goal(self.user, deadline=timezone.localdate() + timezone.timedelta(days=30))
        self._run()
        self.assertFalse(Notification.objects.filter(user=self.user, kind="DEADLINE").exists())

    def test_reminder_is_not_repeated(self):
        from notifications.models import Notification

        make_goal(self.user, deadline=timezone.localdate() + timezone.timedelta(days=1))
        self._run()
        self._run()
        self.assertEqual(Notification.objects.filter(user=self.user, kind="DEADLINE").count(), 1)

    def test_dry_run_sends_nothing(self):
        from notifications.models import Notification

        goal = make_goal(self.user, deadline=timezone.localdate())
        self._run("--dry-run")
        goal.refresh_from_db()
        self.assertFalse(goal.reminder_sent)
        self.assertEqual(Notification.objects.count(), 0)

    def test_weekly_digest_needs_scores(self):
        from notifications.models import Notification
        from progress.models import ComponentScore

        for component in ["MOT", "COG", "ACT", "REF", "CRE"]:
            ComponentScore.objects.create(user=self.user, component=component, value=60)
        self._run("--weekly", "--force-weekly")
        self.assertTrue(Notification.objects.filter(user=self.user, kind="WEEKLY").exists())

    def test_weekly_digest_skips_users_without_scores(self):
        from notifications.models import Notification

        self._run("--weekly", "--force-weekly")
        self.assertFalse(Notification.objects.filter(user=self.user, kind="WEEKLY").exists())
