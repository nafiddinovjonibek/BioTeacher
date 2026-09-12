from django.test import TestCase

# Create your tests here.


class ManageCrudTests(TestCase):
    """Admin uchun universal CRUD (accounts.crud) — yaratish/tahrirlash/arxiv/tiklash."""

    def setUp(self):
        from django.contrib.auth import get_user_model
        from django.urls import reverse

        from core.enums import Role

        self.reverse = reverse
        User = get_user_model()
        self.admin = User.objects.create_user("crud-admin@test.uz", "parol12345")
        self.admin.profile.role = Role.ADMIN
        self.admin.profile.onboarding_done = True
        self.admin.profile.save()
        self.teacher = User.objects.create_user("crud-oqituvchi@test.uz", "parol12345")
        self.teacher.profile.onboarding_done = True
        self.teacher.profile.save()
        self.client.force_login(self.admin)

    def test_teacher_gets_403(self):
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(self.reverse("manage:crud_index")).status_code, 403)
        self.assertEqual(
            self.client.get(self.reverse("manage:crud_list", args=["sections"])).status_code, 403
        )

    def test_every_registered_model_lists(self):
        from accounts.crud import REGISTRY

        self.assertEqual(self.client.get(self.reverse("manage:crud_index")).status_code, 200)
        for key in REGISTRY:
            with self.subTest(key=key):
                url = self.reverse("manage:crud_list", args=[key])
                self.assertEqual(self.client.get(url).status_code, 200)
                self.assertEqual(self.client.get(url + "?q=x").status_code, 200)

    def test_unknown_key_404(self):
        self.assertEqual(self.client.get(self.reverse("manage:crud_list", args=["yoq"])).status_code, 404)

    def test_questionnaires_split_into_tests_and_anketalar(self):
        """Testlar va anketalar alohida bo'limda: kesishmaydi, hech biri yo'qolmaydi."""
        from accounts.crud import get_config
        from diagnostics.models import Questionnaire

        quiz = Questionnaire.objects.create(title="Sinov dars testi", slug="sinov-dars-testi",
                                            kind=Questionnaire.Kind.QUIZ)
        exam = Questionnaire.objects.create(title="Sinov bilim testi", slug="sinov-bilim-testi",
                                            kind=Questionnaire.Kind.TEST)
        likert = Questionnaire.objects.create(title="Sinov likert soni", slug="sinov-likert",
                                              kind=Questionnaire.Kind.LIKERT)

        tests = set(get_config("tests").base_queryset().values_list("pk", flat=True))
        anketalar = set(get_config("questionnaires").base_queryset().values_list("pk", flat=True))
        self.assertEqual(tests, {quiz.pk, exam.pk})
        self.assertEqual(anketalar, {likert.pk})
        self.assertEqual(tests | anketalar,
                         set(Questionnaire.objects.values_list("pk", flat=True)))

        page = self.client.get(self.reverse("manage:crud_list", args=["tests"]))
        self.assertContains(page, "Sinov dars testi")
        self.assertContains(page, "Sinov bilim testi")
        self.assertNotContains(page, "Sinov likert soni")

        # Turi bo'yicha filtr: faqat dars mustahkamlash testlari.
        page = self.client.get(self.reverse("manage:crud_list", args=["tests"]) + "?kind=QUIZ")
        self.assertContains(page, "Sinov dars testi")
        self.assertNotContains(page, "Sinov bilim testi")

        page = self.client.get(self.reverse("manage:crud_list", args=["questionnaires"]))
        self.assertContains(page, "Sinov likert soni")
        self.assertNotContains(page, "Sinov dars testi")

    def test_create_edit_archive_restore_purge_section(self):
        from content.models import Section

        create_url = self.reverse("manage:crud_create", args=["sections"])
        response = self.client.post(create_url, {"title": "Sinov bo'limi", "icon": "📚", "order": 5,
                                                 "is_active": "on", "description": ""})
        self.assertEqual(response.status_code, 302)
        section = Section.objects.get(title="Sinov bo'limi")
        self.assertEqual(section.slug, "sinov-bolimi")  # slug avtomatik

        # Bir xil sarlavha — slug unikal bo'lib qoladi.
        self.client.post(create_url, {"title": "Sinov bo'limi", "icon": "📚", "order": 6, "description": ""})
        self.assertTrue(Section.objects.filter(slug="sinov-bolimi-2").exists())

        edit_url = self.reverse("manage:crud_edit", args=["sections", section.pk])
        self.assertEqual(self.client.get(edit_url).status_code, 200)
        self.client.post(edit_url, {"title": "Yangilangan", "slug": section.slug, "icon": "📚",
                                    "order": 5, "is_active": "on", "description": ""})
        section.refresh_from_db()
        self.assertEqual(section.title, "Yangilangan")

        delete_url = self.reverse("manage:crud_delete", args=["sections", section.pk])
        self.assertEqual(self.client.get(delete_url).status_code, 200)
        self.client.post(delete_url)
        section.refresh_from_db()
        self.assertTrue(section.is_deleted)
        self.assertFalse(Section.objects.filter(pk=section.pk).exists())

        archive = self.client.get(self.reverse("manage:crud_list", args=["sections"]) + "?deleted=1")
        self.assertContains(archive, "Yangilangan")

        self.client.post(self.reverse("manage:crud_restore", args=["sections", section.pk]))
        section.refresh_from_db()
        self.assertFalse(section.is_deleted)

        self.client.post(delete_url)
        self.client.post(self.reverse("manage:crud_purge", args=["sections", section.pk]))
        self.assertFalse(Section.all_objects.filter(pk=section.pk).exists())

    def test_create_user_with_role_and_password(self):
        from django.contrib.auth import get_user_model

        from core.enums import Role

        response = self.client.post(self.reverse("manage:crud_create", args=["users"]), {
            "email": "Yangi@Test.uz", "first_name": "Yangi", "last_name": "Admin",
            "is_active": "on", "email_verified": "on", "role": Role.ADMIN, "roles": [Role.ADMIN],
            "study_arm": "", "new_password": "juda-kuchli-parol-2026", "onboarding_done": "on",
        })
        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.get(email="yangi@test.uz")
        self.assertEqual(user.profile.role, Role.ADMIN)
        self.assertTrue(user.check_password("juda-kuchli-parol-2026"))

        # Parolsiz yangi foydalanuvchi — xato.
        response = self.client.post(self.reverse("manage:crud_create", args=["users"]), {
            "email": "parolsiz@test.uz", "first_name": "A", "last_name": "B", "role": Role.TEACHER,
            "roles": [Role.TEACHER],
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "parol kiriting")

    def test_admin_cannot_delete_self(self):
        response = self.client.post(self.reverse("manage:crud_delete", args=["users", self.admin.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(type(self.admin).objects.filter(pk=self.admin.pk).exists())

    def test_measurement_is_voided_not_deleted(self):
        from diagnostics.models import Measurement

        m = Measurement.objects.create(user=self.teacher, cut="INITIAL", mot=50, cog=50, act=50, ref=50, cre=50)
        self.assertEqual(
            self.client.get(self.reverse("manage:crud_edit", args=["measurements", m.pk])).status_code, 302
        )
        self.client.post(self.reverse("manage:crud_delete", args=["measurements", m.pk]), {"reason": "sinov"})
        m.refresh_from_db()
        self.assertTrue(m.is_void)
        self.assertEqual(m.void_reason, "sinov")

    def test_child_filter_and_initial(self):
        from content.models import Section, Topic

        section = Section.objects.create(title="Filtr bo'limi", slug="filtr-bolimi")
        Topic.objects.create(section=section, title="Ichki mavzu", slug="ichki")
        response = self.client.get(self.reverse("manage:crud_list", args=["topics"]) + f"?section={section.pk}")
        self.assertContains(response, "Ichki mavzu")
        self.assertContains(response, "Filtr bo&#x27;limi")
        response = self.client.get(self.reverse("manage:crud_create", args=["topics"]) + f"?section={section.pk}")
        self.assertContains(response, f'<option value="{section.pk}" selected')

    def test_audit_log_is_read_only(self):
        self.assertEqual(
            self.client.get(self.reverse("manage:crud_create", args=["audit_log"])).status_code, 302
        )
