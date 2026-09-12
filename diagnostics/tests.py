"""Diagnostika oqimi va o'lchov butunligi testlari."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from core.enums import BloomLevel, Component, Cut

from .models import Attempt, Choice, Measurement, Question, Questionnaire, ScoringWeights
from .services import compute_attempt_scores, finish_attempt, get_or_start_attempt, save_answer

User = get_user_model()


def make_likert(slug="anketa-test", per_component=2):
    questionnaire = Questionnaire.objects.create(
        title="Test anketa", slug=slug, kind=Questionnaire.Kind.LIKERT, cut=Cut.INITIAL
    )
    for component in Component.values:
        for index in range(per_component):
            Question.objects.create(
                questionnaire=questionnaire,
                text=f"{component} savol {index}",
                component=component,
                bloom_level=BloomLevel.KNOW,
                reverse_scored=(index == 1),
            )
    return questionnaire


class AnswerScoringTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("talaba@test.uz", "parol12345")
        self.questionnaire = make_likert()

    def test_likert_value_maps_to_percent(self):
        attempt, _ = get_or_start_attempt(self.user, self.questionnaire)
        question = self.questionnaire.questions.filter(reverse_scored=False).first()
        answer = save_answer(attempt, question, value=5)
        self.assertEqual(answer.normalized_percent(), 100.0)

        answer = save_answer(attempt, question, value=1)
        self.assertEqual(answer.normalized_percent(), 0.0)

        answer = save_answer(attempt, question, value=3)
        self.assertEqual(answer.normalized_percent(), 50.0)

    def test_reverse_scored_question_is_inverted(self):
        """FR-09 — teskari savolda 5 ball eng past natijani bildiradi."""
        attempt, _ = get_or_start_attempt(self.user, self.questionnaire)
        question = self.questionnaire.questions.filter(reverse_scored=True).first()
        answer = save_answer(attempt, question, value=5)
        self.assertEqual(answer.normalized_percent(), 0.0)
        answer = save_answer(attempt, question, value=1)
        self.assertEqual(answer.normalized_percent(), 100.0)

    def test_component_scores_are_averaged(self):
        attempt, _ = get_or_start_attempt(self.user, self.questionnaire)
        for question in attempt.questions():
            save_answer(attempt, question, value=1 if question.reverse_scored else 5)
        scores = compute_attempt_scores(attempt)
        for component in Component.values:
            self.assertEqual(scores[component], 100.0)


class AttemptFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("oqish@test.uz", "parol12345")
        self.questionnaire = make_likert()
        ScoringWeights.objects.create(name="Standart", is_active=True)

    def test_unfinished_attempt_is_resumed(self):
        """FR-11 — tugallanmagan urinish davom ettiriladi, yangisi ochilmaydi."""
        first, created_first = get_or_start_attempt(self.user, self.questionnaire)
        second, created_second = get_or_start_attempt(self.user, self.questionnaire)
        self.assertTrue(created_first)
        self.assertFalse(created_second)
        self.assertEqual(first.pk, second.pk)

    def test_finish_creates_measurement_and_recommendations(self):
        attempt, _ = get_or_start_attempt(self.user, self.questionnaire)
        for question in attempt.questions():
            save_answer(attempt, question, value=3)
        attempt, measurement = finish_attempt(attempt)

        self.assertEqual(attempt.status, Attempt.Status.FINISHED)
        self.assertIsNotNone(measurement)
        self.assertEqual(measurement.cut, Cut.INITIAL)
        # FR-12 — eng zaif ikki komponent uchun tavsiya.
        self.assertEqual(measurement.recommendations.filter(is_active=True).count(), 2)

    def test_onboarding_completes_after_first_diagnostic(self):
        """FR-06 — diagnostikadan keyin bloklash olib tashlanadi."""
        self.assertFalse(self.user.profile.onboarding_done)
        attempt, _ = get_or_start_attempt(self.user, self.questionnaire)
        for question in attempt.questions():
            save_answer(attempt, question, value=4)
        finish_attempt(attempt)
        self.user.profile.refresh_from_db()
        self.assertTrue(self.user.profile.onboarding_done)


class MeasurementImmutabilityTests(TestCase):
    """TZ 6.3 — Measurement muzlatilgan."""

    def setUp(self):
        self.user = User.objects.create_user("olchov@test.uz", "parol12345")

    def test_measurement_cannot_be_edited(self):
        measurement = Measurement.objects.create(
            user=self.user, cut=Cut.INITIAL, mot=50, cog=50, act=50, ref=50, cre=50
        )
        measurement.mot = 99
        with self.assertRaises(ValidationError):
            measurement.save()

    def test_measurement_can_be_voided(self):
        measurement = Measurement.objects.create(
            user=self.user, cut=Cut.INITIAL, mot=50, cog=50, act=50, ref=50, cre=50
        )
        measurement.void("test")
        measurement.refresh_from_db()
        self.assertTrue(measurement.is_void)

    def test_weights_snapshot_is_stored(self):
        """SR-05 — vazn o'zgarishi eski o'lchovga ta'sir qilmaydi."""
        ScoringWeights.objects.create(name="Standart", is_active=True)
        first = Measurement.objects.create(
            user=self.user, cut=Cut.INITIAL, mot=100, cog=0, act=0, ref=0, cre=0
        )
        self.assertAlmostEqual(first.sdi, 15.0, places=1)

        ScoringWeights.objects.create(
            name="MOT ustun", mot=1, cog=0, act=0, ref=0, cre=0, is_active=True
        )
        second = Measurement.objects.create(
            user=self.user, cut=Cut.FINAL, mot=100, cog=0, act=0, ref=0, cre=0
        )
        self.assertAlmostEqual(second.sdi, 100.0, places=1)

        first.refresh_from_db()
        self.assertAlmostEqual(first.sdi, 15.0, places=1)  # eski natija o'zgarmadi


class AttemptPermissionTests(TestCase):
    """NFR-12 — boshqaning urinishiga kirish taqiqlanadi."""

    def setUp(self):
        self.owner = User.objects.create_user("egasi@test.uz", "parol12345")
        self.other = User.objects.create_user("begona@test.uz", "parol12345")
        self.questionnaire = make_likert()
        self.attempt, _ = get_or_start_attempt(self.owner, self.questionnaire)

    def test_other_student_cannot_open_attempt(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("diagnostics:take", args=[self.attempt.pk]))
        self.assertEqual(response.status_code, 403)

    def test_other_student_cannot_answer(self):
        self.client.force_login(self.other)
        question = self.attempt.questions()[0]
        response = self.client.post(
            reverse("diagnostics:answer", args=[self.attempt.pk]),
            {"question_id": question.pk, "value": 5},
        )
        self.assertEqual(response.status_code, 403)

    def test_owner_can_open_attempt(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("diagnostics:take", args=[self.attempt.pk]))
        self.assertEqual(response.status_code, 200)


def make_quiz(slug="quiz-test", count=3):
    """Darsning mustahkamlash testi — kesim o'lchovi hosil qilmaydi."""
    questionnaire = Questionnaire.objects.create(
        title="Dars testi", slug=slug, kind=Questionnaire.Kind.QUIZ, cut=Cut.INITIAL
    )
    for index in range(count):
        question = Question.objects.create(
            questionnaire=questionnaire,
            text=f"Savol {index}",
            component=Component.COG,
            bloom_level=BloomLevel.UNDERSTAND,
        )
        Choice.objects.create(question=question, text="To'g'ri", is_correct=True, order=0)
        Choice.objects.create(question=question, text="Xato", is_correct=False, order=1)
    return questionnaire


class LessonQuizDoesNotTouchMeasurementTests(TestCase):
    """SR-06 — dars testi kesim o'lchovini bekor qilmasligi kerak."""

    def setUp(self):
        self.user = User.objects.create_user("talaba@test.uz", "parol12345")
        self.likert = make_likert()
        self.quiz = make_quiz()
        profile = self.user.profile
        profile.onboarding_done = True
        profile.save(update_fields=["onboarding_done"])

    def _finish(self, questionnaire, likert_value=5):
        attempt, _ = get_or_start_attempt(self.user, questionnaire)
        for question in attempt.questions():
            if questionnaire.is_likert:
                save_answer(attempt, question, value=likert_value)
            else:
                save_answer(attempt, question, choice=question.choices.first())
        return finish_attempt(attempt)

    def test_quiz_creates_no_measurement(self):
        _, measurement = self._finish(self.quiz)
        self.assertIsNone(measurement)
        self.assertFalse(Measurement.objects.filter(user=self.user).exists())

    def test_quiz_does_not_void_diagnostic_measurement(self):
        _, diagnostic = self._finish(self.likert)
        self.assertIsNotNone(diagnostic)

        self._finish(self.quiz)

        diagnostic.refresh_from_db()
        self.assertFalse(diagnostic.is_void)
        self.assertEqual(
            Measurement.objects.filter(user=self.user, cut=Cut.INITIAL, is_void=False).count(), 1
        )

    def test_quiz_is_hidden_from_diagnostics_index(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("diagnostics:index"))
        self.assertEqual(response.status_code, 200, response.get("Location", ""))
        slugs = [
            row["q"].slug
            for block in response.context["blocks"]
            for row in block["rows"]
        ]
        self.assertIn(self.likert.slug, slugs)
        self.assertNotIn(self.quiz.slug, slugs)

    def test_quiz_result_does_not_show_foreign_measurement(self):
        self._finish(self.likert)
        attempt, _ = self._finish(self.quiz)
        self.client.force_login(self.user)
        response = self.client.get(reverse("diagnostics:result", args=[attempt.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/biobilim/", response["Location"])
