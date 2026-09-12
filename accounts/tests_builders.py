"""Sodda quruvchilar: test (savol+variant) va inline (rubrika+mezon, bo'lim+mavzu)."""

import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.enums import Role

User = get_user_model()


class BuilderTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("builder-admin@test.uz", "parol12345")
        self.admin.profile.role = Role.ADMIN
        self.admin.profile.onboarding_done = True
        self.admin.profile.save()
        self.client.force_login(self.admin)

    def test_all_builder_pages_open(self):
        from accounts.builders import BUILDER_TITLES

        for kind in BUILDER_TITLES:
            with self.subTest(kind=kind):
                self.assertEqual(self.client.get(reverse("manage:builder_new", args=[kind])).status_code, 200)
        self.assertEqual(self.client.get(reverse("manage:builder_new", args=["yoq"])).status_code, 404)

    def _quiz_payload(self, **extra):
        data = {
            "title": "Hujayra testi", "kind": "TEST", "cut": "INITIAL", "description": "", "instruction": "",
            "question_count": 0, "time_limit_minutes": 10, "shuffle_questions": "on", "is_active": "on",
            "questions_json": json.dumps([
                {"text": "Hujayra qobig'i nimadan iborat?", "component": "COG", "bloom_level": 1,
                 "explanation": "", "choices": [
                     {"text": "Lipid", "is_correct": True}, {"text": "Temir", "is_correct": False},
                     {"text": "", "is_correct": False}]},
                {"text": "Mitoxondriya vazifasi?", "component": "COG", "bloom_level": 2,
                 "explanation": "Energiya", "choices": [
                     {"text": "Energiya", "is_correct": True}, {"text": "Oqsil", "is_correct": False}]},
            ]),
        }
        data.update(extra)
        return data

    def test_create_quiz_with_questions_and_choices(self):
        from diagnostics.models import Choice, Question, Questionnaire

        response = self.client.post(reverse("manage:builder_new", args=["test"]), self._quiz_payload())
        self.assertRedirects(response, reverse("manage:crud_list", args=["tests"]))
        quiz = Questionnaire.objects.get(title="Hujayra testi")
        self.assertEqual(quiz.slug, "hujayra-testi")
        self.assertEqual(quiz.questions.count(), 2)
        first = quiz.questions.order_by("order").first()
        self.assertEqual(first.choices.count(), 2)  # bo'sh variant tashlab yuborildi
        self.assertTrue(first.choices.get(text="Lipid").is_correct)

        # Tahrirlash: 1-savol o'chiriladi (soft), 2-savolga variant qo'shiladi.
        second = quiz.questions.order_by("order").last()
        choice_ids = {c.text: c.pk for c in second.choices.all()}
        payload = self._quiz_payload(questions_json=json.dumps([
            {"id": second.pk, "text": "Mitoxondriya vazifasi? (yangilandi)", "component": "COG",
             "bloom_level": 3, "explanation": "", "choices": [
                 {"id": choice_ids["Energiya"], "text": "ATF", "is_correct": True},
                 {"id": choice_ids["Oqsil"], "text": "Oqsil", "is_correct": False},
                 {"text": "Suv", "is_correct": False}]},
        ]))
        response = self.client.post(reverse("manage:builder_edit", args=["test", quiz.pk]), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(quiz.questions.count(), 1)
        self.assertTrue(Question.all_objects.get(pk=first.pk).is_deleted)
        second.refresh_from_db()
        self.assertEqual(second.text, "Mitoxondriya vazifasi? (yangilandi)")
        self.assertEqual(second.order, 0)
        self.assertEqual(set(second.choices.values_list("text", flat=True)), {"ATF", "Oqsil", "Suv"})
        self.assertEqual(Choice.objects.get(pk=choice_ids["Energiya"]).text, "ATF")  # id saqlandi

        page = self.client.get(reverse("manage:builder_edit", args=["test", quiz.pk]))
        self.assertContains(page, "Mitoxondriya vazifasi? (yangilandi)")
        # Testni tahrirlash sahifasi "Testlar" ro'yxatiga qaytaradi.
        self.assertContains(page, reverse("manage:crud_list", args=["tests"]))

    def test_quiz_validation_errors(self):
        from diagnostics.models import Questionnaire

        bad = self._quiz_payload(questions_json=json.dumps([
            {"text": "", "component": "COG", "bloom_level": 1, "choices": [{"text": "A", "is_correct": False}]},
        ]))
        response = self.client.post(reverse("manage:builder_new", args=["test"]), bad)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1-savol matni bo")
        self.assertContains(response, "kamida 2 ta variant")
        self.assertFalse(Questionnaire.objects.filter(title="Hujayra testi").exists())

        response = self.client.post(reverse("manage:builder_new", args=["test"]),
                                    self._quiz_payload(questions_json="[]"))
        self.assertContains(response, "Kamida bitta savol")

    def test_likert_ignores_choices(self):
        from diagnostics.models import Questionnaire

        payload = self._quiz_payload(kind="LIKERT", title="Anketa", questions_json=json.dumps([
            {"text": "Men darsga tayyorlanaman.", "component": "MOT", "bloom_level": 1,
             "reverse_scored": True, "choices": []},
        ]))
        response = self.client.post(reverse("manage:builder_new", args=["test"]), payload)
        # Likert anketa saqlangach — "Anketalar" ro'yxatiga qaytadi (test emas).
        self.assertRedirects(response, reverse("manage:crud_list", args=["questionnaires"]))
        q = Questionnaire.objects.get(title="Anketa").questions.get()
        self.assertTrue(q.reverse_scored)
        self.assertEqual(q.choices.count(), 0)

    def test_inline_builder_rubric_with_criteria(self):
        from assignments.models import Rubric

        data = {
            "title": "Lab rubrikasi", "slug": "", "description": "", "is_active": "on",
            "criteria-TOTAL_FORMS": "2", "criteria-INITIAL_FORMS": "0",
            "criteria-MIN_NUM_FORMS": "0", "criteria-MAX_NUM_FORMS": "1000",
            "criteria-0-name": "Asoslilik", "criteria-0-hint": "", "criteria-0-weight": "1.0",
            "criteria-0-max_score": "4", "criteria-0-order": "0",
            "criteria-1-name": "Aniqlik", "criteria-1-hint": "", "criteria-1-weight": "2.0",
            "criteria-1-max_score": "3", "criteria-1-order": "1",
        }
        response = self.client.post(reverse("manage:builder_new", args=["rubrika"]), data)
        self.assertEqual(response.status_code, 302)
        rubric = Rubric.objects.get(title="Lab rubrikasi")
        self.assertEqual(rubric.slug, "lab-rubrikasi")
        self.assertEqual(rubric.criteria.count(), 2)

        c1, c2 = rubric.criteria.order_by("order")
        data.update({
            "criteria-TOTAL_FORMS": "2", "criteria-INITIAL_FORMS": "2",
            "criteria-0-id": c1.pk, "criteria-0-rubric": rubric.pk,
            "criteria-1-id": c2.pk, "criteria-1-rubric": rubric.pk, "criteria-1-DELETE": "on",
            "slug": rubric.slug,
        })
        response = self.client.post(reverse("manage:builder_edit", args=["rubrika", rubric.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(list(rubric.criteria.values_list("name", flat=True)), ["Asoslilik"])

    def test_inline_builder_section_with_topics_gets_child_slugs(self):
        from content.models import Section

        data = {
            "title": "Genetika", "slug": "", "description": "", "icon": "DNA", "order": "1", "is_active": "on",
            "topics-TOTAL_FORMS": "2", "topics-INITIAL_FORMS": "0",
            "topics-MIN_NUM_FORMS": "0", "topics-MAX_NUM_FORMS": "1000",
            "topics-0-title": "Irsiyat qonunlari", "topics-0-component": "COG", "topics-0-summary": "",
            "topics-0-order": "0", "topics-0-is_active": "on",
            "topics-1-title": "Irsiyat qonunlari", "topics-1-component": "COG", "topics-1-summary": "",
            "topics-1-order": "1", "topics-1-is_active": "on",
        }
        response = self.client.post(reverse("manage:builder_new", args=["fan"]), data)
        self.assertEqual(response.status_code, 302)
        section = Section.objects.get(title="Genetika")
        slugs = sorted(section.topics.values_list("slug", flat=True))
        self.assertEqual(slugs, ["irsiyat-qonunlari", "irsiyat-qonunlari-2"])

    def test_teacher_cannot_open_builders(self):
        teacher = User.objects.create_user("builder-t@test.uz", "parol12345")
        teacher.profile.onboarding_done = True
        teacher.profile.save()
        self.client.force_login(teacher)
        self.assertEqual(self.client.get(reverse("manage:builder_new", args=["test"])).status_code, 403)
