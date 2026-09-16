"""AI-sokratik: suhbat dvigateli va sahifa («Yoshga oid fiziologiya va gigiyena»)."""

import json

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from reflection.models import ReflectionEntry

from . import engine
from .scenarios import TOPICS

User = get_user_model()


class EngineTests(SimpleTestCase):
    def test_every_topic_can_be_completed(self):
        for key, topic in TOPICS.items():
            with self.subTest(topic=key):
                state, first = engine.start(key)
                self.assertIn(topic["steps"][0]["ask"], first)
                for step in topic["steps"]:
                    # Barcha tushunchalarni o'z ichiga olgan javob — keyingi savolga o'tadi.
                    answer = " va ".join(c["kw"][0] for c in step["concepts"]) + " shuning uchun"
                    engine.reply(state, answer)
                self.assertEqual(state["phase"], "conclude")
                final = engine.reply(state, "Bugun men bu jarayonning sababini o'zim tushunib oldim")
                self.assertEqual(state["phase"], "done")
                self.assertIn(topic["key_points"][0], final)

    def test_hint_then_insight_without_giving_answer_first(self):
        state, _ = engine.start("uyqu")
        step = TOPICS["uyqu"]["steps"][0]
        self.assertEqual(engine.reply(state, "bilmayman"), step["hint"])
        self.assertEqual(state["step"], 0)
        second = engine.reply(state, "bilmadim")
        self.assertIn(step["insight"], second)
        self.assertEqual(state["step"], 1)

    def test_misconception_gets_counter_question(self):
        state, _ = engine.start("skelet")
        text = engine.reply(state, "Menimcha bu irsiy, ota-onasidan o'tgan")
        self.assertIn("Irsiy moyillik bor", text)
        self.assertEqual(state["step"], 0)

    def test_misconception_with_split_words(self):
        state, _ = engine.start("uyqu")
        self.assertIn("uyqusiz qolgan odam", engine.reply(state, "Uyqu — bu vaqtni behuda yo'qotish"))

    def test_partial_answer_probes_missing_concept_once(self):
        state, _ = engine.start("korish")
        first = engine.reply(state, "O'quvchilar kitob va daftarga yaqin masofadan qaraydi")
        self.assertIn("yaqin masofada", first.lower())
        second = engine.reply(state, "Darslikda shunday yozilgan edi")
        self.assertNotEqual(first.split("» ", 1)[-1], second.split(". ", 1)[-1])
        self.assertEqual(state["step"], 0)

    def test_apostrophe_variants_are_matched(self):
        norm = engine.normalize("Yorug‘lik va yorugʻlik, CO₂")
        self.assertTrue(engine.has_any(norm, ["yoruglik"]))
        self.assertTrue(engine.has_any(norm, ["co2"]))

    def test_free_question_detects_topic_or_uses_generic_flow(self):
        state, _ = engine.start(None)
        engine.reply(state, "Nega o'quvchilar 6-darsda tez charchaydi?")
        self.assertEqual(state["topic"], "nerv")

        state, _ = engine.start(None)
        text = engine.reply(state, "Qushlar qanday qilib yo'lni topadi?")
        self.assertIsNone(state["topic"])
        self.assertIn("Qushlar qanday qilib", text)
        for _ in engine.GENERIC_STEPS:
            engine.reply(state, "Menimcha ular Quyosh va magnit maydoniga qarab mo'ljal oladi")
        self.assertEqual(state["phase"], "conclude")

    def test_finish_shortcut(self):
        state, _ = engine.start("oziqlanish")
        self.assertEqual(engine.reply(state, "Suhbatni yakunlash"), engine.CONCLUDE_ASK)
        self.assertEqual(state["phase"], "conclude")


class ChatViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("sokratik@test.uz", "parol12345")
        self.user.profile.onboarding_done = True
        self.user.profile.save()
        self.client.force_login(self.user)

    def post_json(self, name, data):
        response = self.client.post(reverse(name), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_page_renders_and_menu_item_active(self):
        response = self.client.get(reverse("socratic:chat"))
        self.assertContains(response, "AI-sokratik yordamchiman")
        self.assertContains(response, 'data-topic="skelet"')
        self.assertRedirects(self.client.get("/bolim/ai-sokratik/"), reverse("socratic:chat"))

    def test_conversation_is_kept_in_session_and_saved_to_journal(self):
        data = self.post_json("socratic:start", {"topic": "uyqu"})
        self.assertEqual(data["progress"], {"step": 0, "total": 4, "phase": "dialog", "topic": "uyqu",
                                            "title": "Uyqu gigiyenasi"})
        data = self.post_json("socratic:message", {"message": "Suhbatni yakunlash"})
        self.assertEqual(data["progress"]["phase"], "conclude")

        # Yakunlanmagan suhbat saqlanmaydi.
        self.client.post(reverse("socratic:save"))
        self.assertFalse(ReflectionEntry.objects.exists())

        data = self.post_json("socratic:message", {"message": "Uyqu yetishmasa diqqat pasayadi, shuning uchun kun tartibi muhim"})
        self.assertTrue(data["can_save"])
        self.assertContains(self.client.get(reverse("socratic:chat")), "Uyqu yetishmasa diqqat")

        response = self.client.post(reverse("socratic:save"))
        entry = ReflectionEntry.objects.get(user=self.user)
        self.assertRedirects(response, reverse("reflection:detail", args=[entry.pk]))
        self.assertEqual(entry.kind, ReflectionEntry.Kind.FREE)
        self.assertIn("kun tartibi muhim", entry.q1)
        self.assertIn("AI-sokratik:", entry.free_text)
        self.assertEqual(entry.tags, "ai-sokratik,uyqu")
        # Saqlangach yangi suhbat boshlanadi.
        self.assertEqual(self.post_json("socratic:message", {"message": "Nerv tizimi va charchash haqida gaplashamiz"})["progress"]["topic"], "nerv")

    def test_form_fallback_without_js(self):
        response = self.client.post(reverse("socratic:message"), {"message": "Miyopiya nima?"})
        self.assertRedirects(response, reverse("socratic:chat"))
        self.assertEqual(self.client.session["socratic"]["topic"], "korish")

    def test_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("socratic:chat")).status_code, 302)
