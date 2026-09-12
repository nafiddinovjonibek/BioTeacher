"""Avtomatik slug/order va drag & drop tartiblash."""

import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.enums import Role

User = get_user_model()


class AutoOrderTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("order-admin@test.uz", "parol12345")
        self.admin.profile.role = Role.ADMIN
        self.admin.profile.onboarding_done = True
        self.admin.profile.save()
        self.client.force_login(self.admin)

    def test_slug_and_order_are_hidden_and_auto(self):
        from content.models import Section

        page = self.client.get(reverse("manage:crud_create", args=["sections"]))
        self.assertNotContains(page, 'name="slug"')
        self.assertNotContains(page, 'name="order"')

        url = reverse("manage:crud_create", args=["sections"])
        for title in ["Birinchi bo'lim", "Ikkinchi bo'lim", "Birinchi bo'lim"]:
            self.client.post(url, {"title": title, "icon": "A", "description": "", "is_active": "on"})
        rows = list(Section.objects.filter(title__contains="bo'lim").order_by("order").values_list("slug", "order"))
        self.assertEqual(rows, [("birinchi-bolim", 0), ("ikkinchi-bolim", 1), ("birinchi-bolim-2", 2)])

    def test_child_order_scoped_to_parent(self):
        from content.models import Section, Topic

        a = Section.objects.create(title="A", slug="a")
        b = Section.objects.create(title="B", slug="b")
        url = reverse("manage:crud_create", args=["topics"])
        for section, title in [(a, "A1"), (a, "A2"), (b, "B1")]:
            self.client.post(url, {"section": section.pk, "title": title, "component": "COG", "summary": "", "is_active": "on"})
        self.assertEqual(list(Topic.objects.filter(section=a).order_by("order").values_list("title", "order")),
                         [("A1", 0), ("A2", 1)])
        self.assertEqual(Topic.objects.get(title="B1").order, 0)

    def test_reorder_endpoint(self):
        from content.models import Section

        s1 = Section.objects.create(title="S1", slug="s1", order=0)
        s2 = Section.objects.create(title="S2", slug="s2", order=1)
        s3 = Section.objects.create(title="S3", slug="s3", order=2)
        response = self.client.post(
            reverse("manage:crud_reorder", args=["sections"]),
            json.dumps({"ids": [s3.pk, s1.pk, s2.pk]}), content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(list(Section.objects.order_by("order").values_list("title", flat=True)), ["S3", "S1", "S2"])

        # GET ruxsat yo'q, tartibsiz model 404.
        self.assertEqual(self.client.get(reverse("manage:crud_reorder", args=["sections"])).status_code, 405)
        self.assertEqual(self.client.post(reverse("manage:crud_reorder", args=["users"]),
                                          "{}", content_type="application/json").status_code, 404)

    def test_list_shows_drag_handle_for_orderable_only(self):
        self.assertContains(self.client.get(reverse("manage:crud_list", args=["sections"])), "drag-handle")
        self.assertNotContains(self.client.get(reverse("manage:crud_list", args=["users"])), "drag-handle")

    def test_inline_builder_respects_dragged_order(self):
        from assignments.models import Rubric

        data = {
            "title": "Tartib rubrikasi", "description": "", "is_active": "on",
            "criteria-TOTAL_FORMS": "2", "criteria-INITIAL_FORMS": "0",
            "criteria-MIN_NUM_FORMS": "0", "criteria-MAX_NUM_FORMS": "1000",
            "criteria-0-name": "Birinchi yozilgan", "criteria-0-hint": "", "criteria-0-weight": "1",
            "criteria-0-max_score": "4", "criteria-0-ORDER": "2",
            "criteria-1-name": "Ikkinchi yozilgan", "criteria-1-hint": "", "criteria-1-weight": "1",
            "criteria-1-max_score": "4", "criteria-1-ORDER": "1",
        }
        response = self.client.post(reverse("manage:builder_new", args=["rubrika"]), data)
        self.assertEqual(response.status_code, 302)
        rubric = Rubric.objects.get(title="Tartib rubrikasi")
        self.assertEqual(list(rubric.criteria.order_by("order").values_list("name", "order")),
                         [("Ikkinchi yozilgan", 0), ("Birinchi yozilgan", 1)])

    def test_teacher_cannot_reorder(self):
        teacher = User.objects.create_user("order-t@test.uz", "parol12345")
        teacher.profile.onboarding_done = True
        teacher.profile.save()
        self.client.force_login(teacher)
        response = self.client.post(reverse("manage:crud_reorder", args=["sections"]),
                                    json.dumps({"ids": []}), content_type="application/json")
        self.assertEqual(response.status_code, 403)


class RailMenuTests(TestCase):
    """Yon panel: admin (yoki superuser) — faqat boshqaruv; o'qituvchi — faqat o'quv menyusi."""

    def _rail(self, user):
        self.client.force_login(user)
        return self.client.get(reverse("home:cabinet")).content.decode()

    def test_superuser_defaults_to_admin_and_menus_never_mix(self):
        su = User.objects.create_superuser("su-rail@test.uz", "parol12345")
        self.assertEqual(su.profile.role, Role.ADMIN)  # signal avtomatik ADMIN qiladi
        html = self._rail(su)
        self.assertIn("Tekshirish navbati", html)
        self.assertNotIn("Refleksiya kundaligi", html)

    def test_teacher_sees_only_learner_menu(self):
        t = User.objects.create_user("t-rail@test.uz", "parol12345")
        t.profile.onboarding_done = True
        t.profile.save()
        html = self._rail(t)
        self.assertIn("Refleksiya kundaligi", html)
        self.assertNotIn("Tekshirish navbati", html)

    def test_admin_sees_only_admin_menu(self):
        a = User.objects.create_user("a-rail@test.uz", "parol12345")
        a.profile.role = Role.ADMIN
        a.profile.onboarding_done = True
        a.profile.save()
        html = self._rail(a)
        self.assertIn("Tekshirish navbati", html)
        self.assertNotIn("Refleksiya kundaligi", html)



class MultiRoleTests(TestCase):
    """Bir foydalanuvchida bir nechta rol va ular orasida almashish."""

    def setUp(self):
        self.user = User.objects.create_user("multi@test.uz", "parol12345")
        self.user.profile.set_roles([Role.TEACHER, Role.ADMIN], active=Role.ADMIN)
        self.user.profile.onboarding_done = True
        self.user.profile.save()
        self.client.force_login(self.user)

    def _rail(self):
        return self.client.get(reverse("home:cabinet")).content.decode()

    def test_switcher_shown_and_menus_follow_active_role(self):
        html = self._rail()
        self.assertIn("Rejim", html)
        self.assertIn("Tekshirish navbati", html)
        self.assertNotIn("Refleksiya kundaligi", html)
        self.assertEqual(self.client.get(reverse("manage:students")).status_code, 200)

        response = self.client.post(reverse("accounts:switch_role"), {"role": Role.TEACHER})
        self.assertRedirects(response, reverse("home:dashboard"), fetch_redirect_response=False)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.role, Role.TEACHER)

        html = self._rail()
        self.assertIn("Refleksiya kundaligi", html)
        self.assertNotIn("Tekshirish navbati", html)
        # O'qituvchi rejimida admin sahifalari yopiq.
        self.assertEqual(self.client.get(reverse("manage:students")).status_code, 403)
        self.assertEqual(self.client.get(reverse("home:dashboard")).status_code, 200)

        self.client.post(reverse("accounts:switch_role"), {"role": Role.ADMIN})
        self.assertRedirects(self.client.get(reverse("home:dashboard")), reverse("manage:students"))

    def test_cannot_switch_to_ungranted_role(self):
        teacher = User.objects.create_user("only-t@test.uz", "parol12345")
        teacher.profile.onboarding_done = True
        teacher.profile.save()
        self.client.force_login(teacher)
        self.assertNotIn("Rejim", self._rail())
        self.client.post(reverse("accounts:switch_role"), {"role": Role.ADMIN})
        teacher.profile.refresh_from_db()
        self.assertEqual(teacher.profile.role, Role.TEACHER)
        self.assertEqual(self.client.get(reverse("manage:students")).status_code, 403)

    def test_switch_requires_post(self):
        self.assertEqual(self.client.get(reverse("accounts:switch_role")).status_code, 405)

    def test_switch_allowed_during_onboarding(self):
        """Admin o'qituvchi rejimiga o'tib onboarding'da qolib ketmasligi kerak."""
        self.user.profile.onboarding_done = False
        self.user.profile.save()
        self.client.post(reverse("accounts:switch_role"), {"role": Role.TEACHER})
        self.assertRedirects(self.client.get(reverse("home:dashboard")), reverse("accounts:onboarding"))
        response = self.client.post(reverse("accounts:switch_role"), {"role": Role.ADMIN})
        self.assertEqual(response.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.role, Role.ADMIN)

    def test_admin_in_admin_mode_still_counts_as_learner(self):
        """Admin rejimida turgan, lekin o'qituvchi roli bor foydalanuvchi e'lon/eslatmalarni oladi."""
        from accounts.services import learner_queryset

        self.assertIn(self.user, list(learner_queryset()))
        admin_only = User.objects.create_user("admin-only@test.uz", "parol12345")
        admin_only.profile.set_roles([Role.ADMIN])
        admin_only.profile.save()
        self.assertNotIn(admin_only, list(learner_queryset()))

    def test_manage_form_sets_multiple_roles(self):
        self.client.post(reverse("accounts:switch_role"), {"role": Role.ADMIN})
        response = self.client.post(reverse("manage:crud_create", args=["users"]), {
            "email": "ikki-rol@test.uz", "first_name": "Ikki", "last_name": "Rol",
            "is_active": "on", "email_verified": "on",
            "roles": [Role.TEACHER, Role.ADMIN], "role": Role.TEACHER,
            "study_arm": "", "new_password": "juda-kuchli-parol-2026",
        })
        self.assertEqual(response.status_code, 302)
        profile = User.objects.get(email="ikki-rol@test.uz").profile
        self.assertEqual(profile.role, Role.TEACHER)
        self.assertEqual(profile.role_list, [Role.TEACHER, Role.ADMIN])

        # Faol rol belgilanmagan rollar ichida bo'lmasa — xato.
        response = self.client.post(reverse("manage:crud_create", args=["users"]), {
            "email": "xato-rol@test.uz", "first_name": "X", "last_name": "R",
            "roles": [Role.TEACHER], "role": Role.ADMIN, "new_password": "juda-kuchli-parol-2026",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "belgilangan rollar ichida")
