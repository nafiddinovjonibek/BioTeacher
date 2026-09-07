"""Refleksiya sifatini baholash testlari (FR-40, FR-41)."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ReflectionEntry
from .services import save_with_score, score_reflection

User = get_user_model()

GOOD = {
    "q1": ("Bugun men fotosintezning yorug'lik bosqichi aynan tilakoid membranasida kechishini "
           "aniq tushundim. Ilgari men butun jarayon stromada kechadi deb o'ylardim, chunki "
           "darslikda ikkala bosqich bitta sxemada berilgan edi."),
    "q2": ("Tajriba rejasini tuzishda nazorat namunasini ko'zda tutdim — bu yaxshi chiqdi, "
           "chunki natijani boshqa omillar bilan chalkashtirmaslik imkonini berdi."),
    "q3": ("Men hali natijani miqdoriy o'lchashni yaxshi bilmayman. Darsda o'quvchilarga aniq "
           "o'lchov birligini bera olmadim, shuning uchun ularning xulosasi sifatiy bo'lib qoldi."),
    "q4": ("Keyingi safar tajribadan oldin o'lchov jadvalini tayyorlayman va o'quvchilarga "
           "massani tarozida o'lchashni topshiraman."),
}

POOR = {"q1": "Yaxshi", "q2": "Zo'r", "q3": "Bilmadim", "q4": "Ha"}


class ReflectionScoringTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("refleks@test.uz", "parol12345")

    def _entry(self, data):
        return ReflectionEntry(user=self.user, kind=ReflectionEntry.Kind.TASK, **data)

    def test_good_reflection_scores_high(self):
        score, detail = score_reflection(self._entry(GOOD))
        self.assertGreaterEqual(score, 70)
        self.assertGreaterEqual(detail["completeness"], 90)

    def test_template_answers_score_low(self):
        score, detail = score_reflection(self._entry(POOR))
        self.assertLess(score, 30)
        self.assertEqual(detail["completeness"], 0.0)

    def test_hints_are_generated_for_weak_criteria(self):
        _, detail = score_reflection(self._entry(POOR))
        self.assertTrue(detail["hints"])

    def test_good_reflection_needs_no_hints(self):
        _, detail = score_reflection(self._entry(GOOD))
        self.assertEqual(detail["hints"], [])

    def test_analysis_criterion_detects_causal_markers(self):
        with_cause = self._entry({**GOOD})
        without_cause = self._entry({
            "q1": "Men bugun fotosintez mavzusini o'rgandim va sxemani ko'rib chiqdim, mavzu qiziq edi.",
            "q2": "Tajribani bajardim, hammasi rejaga muvofiq ketdi va natija olindi nihoyat.",
            "q3": "Yana ko'proq mashq qilishim kerak, ayniqsa amaliy topshiriqlar ustida ishlashim.",
            "q4": "Ko'proq harakat qilaman va materialni yana bir bor ko'rib chiqaman albatta.",
        })
        _, detail_with = score_reflection(with_cause)
        _, detail_without = score_reflection(without_cause)
        self.assertGreater(detail_with["analysis"], detail_without["analysis"])


class ReflectionEffectTests(TestCase):
    """FR-41 — refleksiya sifati REF komponentiga ta'sir qiladi."""

    def setUp(self):
        self.user = User.objects.create_user("tasir@test.uz", "parol12345")

    def test_saving_reflection_updates_ref_component(self):
        from progress.models import ComponentScore

        entry = ReflectionEntry.objects.create(
            user=self.user, kind=ReflectionEntry.Kind.TASK, **GOOD
        )
        save_with_score(entry)

        score = ComponentScore.objects.get(user=self.user, component="REF")
        self.assertGreater(score.value, 0)
        self.assertEqual(score.value, entry.quality_score)

    def test_activity_is_logged(self):
        from progress.models import ActivityLog

        entry = ReflectionEntry.objects.create(
            user=self.user, kind=ReflectionEntry.Kind.TASK, **GOOD
        )
        save_with_score(entry)
        self.assertTrue(
            ActivityLog.objects.filter(user=self.user, action=ActivityLog.Action.REFLECTION).exists()
        )


class ReflectionFormTests(TestCase):
    """FR-40 — minimal hajm nazorati."""

    def setUp(self):
        self.user = User.objects.create_user("forma@test.uz", "parol12345")
        self.user.profile.onboarding_done = True
        self.user.profile.save()
        self.client.force_login(self.user)

    def test_short_reflection_is_rejected(self):
        response = self.client.post(reverse("reflection:create_free"), {"free_text": "Yaxshi"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ReflectionEntry.objects.count(), 0)

    def test_long_enough_reflection_is_saved(self):
        text = ("Bugun dars loyihasini tuzishda maqsadni o'lchanadigan qilib yozishni mashq qildim. "
                "Avval maqsadni o'qituvchi faoliyati orqali yozar edim, endi o'quvchi harakati "
                "orqali yozyapman va buni tekshirish osonroq.")
        response = self.client.post(reverse("reflection:create_free"), {"free_text": text})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ReflectionEntry.objects.count(), 1)


class ReflectionPrivacyTests(TestCase):
    """FR-42 — kundalik faqat talaba va uning mentoriga ko'rinadi."""

    def setUp(self):
        self.owner = User.objects.create_user("egasi2@test.uz", "parol12345")
        self.other = User.objects.create_user("begona2@test.uz", "parol12345")
        for user in (self.owner, self.other):
            user.profile.onboarding_done = True
            user.profile.save()
        self.entry = ReflectionEntry.objects.create(
            user=self.owner, kind=ReflectionEntry.Kind.TASK, **GOOD
        )

    def test_other_student_gets_403(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("reflection:detail", args=[self.entry.pk]))
        self.assertEqual(response.status_code, 403)

    def test_owner_can_read(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("reflection:detail", args=[self.entry.pk]))
        self.assertEqual(response.status_code, 200)
