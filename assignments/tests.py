"""Topshiriq sikli, baholash va ruxsatlar testlari."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Enrollment, StudyGroup
from core.enums import BloomLevel, Component, Module, Role

from .models import Assignment, Criterion, Rubric, Score, Submission
from .services import apply_scores, assessment_gap_stats, finalize_submission, rubric_percent

User = get_user_model()


def make_rubric():
    rubric = Rubric.objects.create(title="Test rubrika", slug="test-rubrika")
    Criterion.objects.create(rubric=rubric, name="Mezon A", max_score=4, weight=1.0, order=0)
    Criterion.objects.create(rubric=rubric, name="Mezon B", max_score=4, weight=1.0, order=1)
    return rubric


def make_assignment(rubric, slug="test-topshiriq"):
    return Assignment.objects.create(
        module=Module.LAB, kind=Assignment.Kind.LAB4, title="Test topshiriq", slug=slug,
        body="Topshiriq matni", component=Component.COG, bloom_level=BloomLevel.APPLY,
        rubric=rubric, reference_solution="Etalon yechim matni",
    )


class RubricScoringTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user("baho@test.uz", "parol12345")
        self.rubric = make_rubric()
        self.assignment = make_assignment(self.rubric)
        self.submission = Submission.objects.create(
            assignment=self.assignment, student=self.student
        )

    def test_full_marks_give_hundred_percent(self):
        values = {c.id: 4 for c in self.rubric.criteria.all()}
        percent = apply_scores(self.submission, Score.Scorer.SELF, values)
        self.assertEqual(percent, 100.0)

    def test_zero_marks_give_zero(self):
        values = {c.id: 0 for c in self.rubric.criteria.all()}
        self.assertEqual(apply_scores(self.submission, Score.Scorer.SELF, values), 0.0)

    def test_weighted_criteria_are_respected(self):
        heavy = self.rubric.criteria.first()
        heavy.weight = 3.0
        heavy.save()
        light = self.rubric.criteria.last()
        apply_scores(self.submission, Score.Scorer.SELF, {heavy.id: 4, light.id: 0})
        # (4*3 + 0*1) / (4*3 + 4*1) = 12/16 = 75%
        self.assertEqual(rubric_percent(self.submission, Score.Scorer.SELF), 75.0)

    def test_score_out_of_range_is_clamped(self):
        values = {c.id: 99 for c in self.rubric.criteria.all()}
        self.assertEqual(apply_scores(self.submission, Score.Scorer.SELF, values), 100.0)

    def test_final_percent_prefers_mentor(self):
        criteria = list(self.rubric.criteria.all())
        apply_scores(self.submission, Score.Scorer.SELF, {c.id: 4 for c in criteria})
        apply_scores(self.submission, Score.Scorer.MENTOR, {c.id: 2 for c in criteria})
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.final_percent, 50.0)

    def test_assessment_gap(self):
        """FR-25 — o'z bahosi va mentor bahosi farqi."""
        criteria = list(self.rubric.criteria.all())
        apply_scores(self.submission, Score.Scorer.SELF, {c.id: 4 for c in criteria})
        apply_scores(self.submission, Score.Scorer.MENTOR, {c.id: 3 for c in criteria})
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.assessment_gap, 25.0)

        stats = assessment_gap_stats(self.student)
        self.assertEqual(stats["count"], 1)
        self.assertEqual(stats["average"], 25.0)


class SubmissionLifecycleTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user("sikl@test.uz", "parol12345")
        self.rubric = make_rubric()
        self.assignment = make_assignment(self.rubric)
        self.submission = Submission.objects.create(
            assignment=self.assignment, student=self.student, payload={"hypothesis": "x"}
        )

    def test_reference_hidden_before_submit(self):
        """FR-24 — etalon yechim faqat yuborilgandan keyin."""
        self.assertFalse(self.submission.can_see_reference())
        finalize_submission(self.submission)
        self.assertTrue(self.submission.can_see_reference())

    def test_submitted_work_is_locked(self):
        finalize_submission(self.submission)
        self.submission.refresh_from_db()
        self.assertTrue(self.submission.is_locked)

    def test_reopen_makes_editable_again(self):
        finalize_submission(self.submission)
        self.submission.reopen_allowed = True
        self.submission.save()
        self.assertTrue(self.submission.is_editable)

    def test_submitting_updates_component_score(self):
        from progress.models import ComponentScore

        criteria = list(self.rubric.criteria.all())
        apply_scores(self.submission, Score.Scorer.SELF, {c.id: 3 for c in criteria})
        finalize_submission(self.submission)
        score = ComponentScore.objects.get(user=self.student, component=Component.COG)
        self.assertEqual(score.value, 75.0)

    def test_answer_rows_use_step_labels(self):
        rows = self.submission.answer_rows()
        self.assertEqual(rows[0]["label"], "1. Taxmin")
        self.assertEqual(rows[0]["text"], "x")


class SubmissionPermissionTests(TestCase):
    """NFR-12 / FR-00 — talaba boshqaning ishini ko'rmaydi."""

    def setUp(self):
        self.rubric = make_rubric()
        self.assignment = make_assignment(self.rubric)
        self.owner = User.objects.create_user("ega3@test.uz", "parol12345")
        self.other = User.objects.create_user("begona3@test.uz", "parol12345")
        self.mentor = User.objects.create_user("mentor3@test.uz", "parol12345")
        self.mentor.profile.role = Role.TEACHER
        self.mentor.profile.save()

        self.group = StudyGroup.objects.create(name="G-1", teacher=self.mentor)
        self.owner.profile.group = self.group
        self.owner.profile.onboarding_done = True
        self.owner.profile.save()
        self.other.profile.onboarding_done = True
        self.other.profile.save()
        Enrollment.objects.create(student=self.owner, group=self.group)

        self.submission = Submission.objects.create(
            assignment=self.assignment, student=self.owner, status=Submission.Status.SUBMITTED
        )

    def test_other_student_cannot_view_submission(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("assignments:submission", args=[self.submission.pk]))
        self.assertEqual(response.status_code, 403)

    def test_owner_can_view_submission(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("assignments:submission", args=[self.submission.pk]))
        self.assertEqual(response.status_code, 200)

    def test_mentor_of_group_can_view_and_grade(self):
        self.client.force_login(self.mentor)
        self.assertEqual(
            self.client.get(reverse("assignments:submission", args=[self.submission.pk])).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("assignments:grade", args=[self.submission.pk])).status_code,
            200,
        )

    def test_foreign_mentor_cannot_grade(self):
        stranger = User.objects.create_user("boshqa-mentor@test.uz", "parol12345")
        stranger.profile.role = Role.TEACHER
        stranger.profile.save()
        self.client.force_login(stranger)
        response = self.client.get(reverse("assignments:grade", args=[self.submission.pk]))
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_open_review_queue(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("assignments:queue"))
        self.assertEqual(response.status_code, 403)
