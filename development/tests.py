"""«3-blok: O'z-o'zini rivojlantirish»: sahifalar, namunalar va admin boshqaruvi (CRUD)."""

import re
from html import unescape

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from assignments.models import Assignment, Rubric
from core.enums import Module, Role

from .models import PlotResource, Simulation

User = get_user_model()

# 1x1 PNG
PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
       b"\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x03\x00\x08\xfc\x02\xfe\xa7\x9a\xa0\xa0\x00\x00\x00\x00IEND\xaeB`\x82")


def active_labels(html):
    nav = html[html.index('aria-label="Asosiy menyu"'):html.find("</nav>")]
    found = re.findall(r'aria-current="page"[^>]*>.*?class="rail-label[^"]*">([^<]+)<', nav, re.S)
    return [unescape(label) for label in found]


class SamplesTests(TestCase):
    def test_migration_seeds_samples(self):
        self.assertGreaterEqual(Simulation.objects.count(), 4)
        self.assertGreaterEqual(PlotResource.objects.count(), 5)
        sim = Simulation.objects.get(slug="3d-hayvon-hujayrasi")
        self.assertTrue(sim.picture_url.endswith("img/sim3d/hayvon-hujayrasi.svg"))
        self.assertIn(("Yadro", "irsiy axborotni (DNK) saqlaydi va hujayra faoliyatini boshqaradi"), sim.part_rows())

    def test_plot_body_blocks(self):
        blocks = PlotResource.objects.get(slug="urug-unuvchanligini-aniqlash").blocks()
        self.assertEqual(blocks[0]["heading"], "Maqsad")
        self.assertTrue(blocks[0]["lines"][0].startswith("O'quvchilar"))


class TeacherPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("teacher-dev@test.uz", "parol12345")
        self.user.profile.onboarding_done = True
        self.user.profile.save()
        self.client.force_login(self.user)

    def test_pages_render_without_admin_tools(self):
        sim = Simulation.objects.first()
        resource = PlotResource.objects.first()
        for url, label in [
            (reverse("development:simulations"), "3D simulyatsiyalar"),
            (reverse("development:simulation", args=[sim.slug]), "3D simulyatsiyalar"),
            (reverse("development:plot"), "Maktab o‘quv-tajriba uchastkasi resurslari"),
            (reverse("development:plot") + "?tur=GUIDE&mavsum=SPRING", "Maktab o‘quv-tajriba uchastkasi resurslari"),
            (reverse("development:plot_resource", args=[resource.slug]), "Maktab o‘quv-tajriba uchastkasi resurslari"),
        ]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                html = response.content.decode()
                self.assertEqual(active_labels(html), [label])
                self.assertNotIn('class="admin-tools"', html)
                self.assertNotIn("Administrator rejimi", html)

    def test_inactive_and_archived_are_hidden(self):
        sim = Simulation.objects.first()
        sim.is_active = False
        sim.save()
        self.assertNotContains(self.client.get(reverse("development:simulations")), sim.title)
        self.assertEqual(self.client.get(reverse("development:simulation", args=[sim.slug])).status_code, 404)
        resource = PlotResource.objects.first()
        resource.delete()  # arxiv
        self.assertEqual(self.client.get(reverse("development:plot_resource", args=[resource.slug])).status_code, 404)

    def test_old_upcoming_urls_redirect(self):
        self.assertRedirects(self.client.get(reverse("home:upcoming", args=["3d-simulyatsiyalar"])),
                             reverse("development:simulations"))
        self.assertRedirects(self.client.get(reverse("home:upcoming", args=["tajriba-uchastkasi"])),
                             reverse("development:plot"))

    def test_teacher_cannot_use_crud(self):
        self.assertEqual(self.client.get(reverse("manage:crud_create", args=["simulations"])).status_code, 403)


class AdminManageTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin-dev@test.uz", "parol12345")
        self.admin.profile.set_roles([Role.TEACHER, Role.ADMIN], active=Role.ADMIN)
        self.admin.profile.onboarding_done = True
        self.admin.profile.save()
        self.client.force_login(self.admin)
        self.rubric = Rubric.objects.get_or_create(slug="vizual-tahlil", defaults={"title": "Vizual tahlil"})[0]

    def test_admin_sees_tools_on_all_four_pages(self):
        for url, key in [
            (reverse("assignments:cases"), "visual_cases"),
            (reverse("assignments:module", args=[Module.LAB]), "practice_tasks"),
            (reverse("development:simulations"), "simulations"),
            (reverse("development:plot"), "plot_resources"),
        ]:
            with self.subTest(url=url):
                html = self.client.get(url).content.decode()
                self.assertIn(reverse("manage:crud_create", args=[key]), html)
                self.assertIn("Administrator rejimi", html)

    def test_crud_index_has_block3_group(self):
        html = self.client.get(reverse("manage:crud_index")).content.decode()
        self.assertIn("3-blok: O‘z-o‘zini rivojlantirish", html)
        for key in ["visual_cases", "practice_tasks", "simulations", "plot_resources"]:
            self.assertIn(reverse("manage:crud_list", args=[key]), html)

    def test_create_simulation_requires_image_and_returns_to_page(self):
        url = reverse("manage:crud_create", args=["simulations"]) + "?next=" + reverse("development:simulations")
        data = {"title": "Yurak modeli", "summary": "To'rt kamerali yurak", "parts": "Chap qorincha — qonni aortaga haydaydi",
                "task": "Kameralarni sanang", "is_active": "on"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "3D tasvirni yuklang.")

        data["image"] = SimpleUploadedFile("yurak.png", PNG, content_type="image/png")
        with self.settings(MEDIA_ROOT=self._tmp()):
            response = self.client.post(url, data)
            self.assertRedirects(response, reverse("development:simulations"), fetch_redirect_response=False)
            sim = Simulation.objects.get(title="Yurak modeli")
            self.assertEqual(sim.slug, "yurak-modeli")
            self.assertEqual(sim.part_rows(), [("Chap qorincha", "qonni aortaga haydaydi")])
            self.assertContains(self.client.get(reverse("development:simulations")), "Yurak modeli")

    def test_simulation_link_field_is_editable_and_shown(self):
        sim = Simulation.objects.get(slug="3d-hayvon-hujayrasi")
        form_html = self.client.get(reverse("manage:crud_create", args=["simulations"])).content.decode()
        self.assertIn('name="url"', form_html)
        self.assertIn("Havola", form_html)

        edit = reverse("manage:crud_edit", args=["simulations", sim.pk])
        response = self.client.post(edit, {
            "title": sim.title, "section": sim.section_id or "", "image_alt": sim.image_alt,
            "url": "https://sketchfab.com/3d-models/animal-cell", "summary": sim.summary,
            "body": sim.body, "parts": sim.parts, "task": sim.task, "is_active": "on",
        })
        self.assertEqual(response.status_code, 302)
        sim.refresh_from_db()
        self.assertEqual(sim.url, "https://sketchfab.com/3d-models/animal-cell")

        page = self.client.get(reverse("development:simulation", args=[sim.slug]))
        self.assertContains(page, sim.url)
        self.assertContains(page, "Interaktiv 3D modelni ochish")
        self.assertContains(self.client.get(reverse("development:simulations")), "Interaktiv")

    def test_edit_and_delete_plot_resource(self):
        resource = PlotResource.objects.first()
        page = reverse("development:plot")
        edit = reverse("manage:crud_edit", args=["plot_resources", resource.pk]) + "?next=" + page
        response = self.client.post(edit, {
            "title": "Yangi nom", "kind": "DIARY", "season": "AUTUMN", "grade": "8-sinf", "duration": "",
            "summary": "Qisqa", "body": "Matn", "url": "", "is_active": "on",
        })
        self.assertRedirects(response, page, fetch_redirect_response=False)
        resource.refresh_from_db()
        self.assertEqual((resource.title, resource.kind, resource.season), ("Yangi nom", "DIARY", "AUTUMN"))

        delete = reverse("manage:crud_delete", args=["plot_resources", resource.pk]) + "?next=" + page
        self.assertRedirects(self.client.post(delete), page, fetch_redirect_response=False)
        self.assertFalse(PlotResource.objects.filter(pk=resource.pk).exists())
        self.assertTrue(PlotResource.all_objects.filter(pk=resource.pk, is_deleted=True).exists())

    def test_next_must_be_local(self):
        resource = PlotResource.objects.first()
        url = reverse("manage:crud_delete", args=["plot_resources", resource.pk]) + "?next=https://evil.example/"
        self.assertRedirects(self.client.post(url), reverse("manage:crud_list", args=["plot_resources"]),
                             fetch_redirect_response=False)

    def test_visual_case_gets_hidden_module_and_default_rubric(self):
        form = self.client.get(reverse("manage:crud_create", args=["visual_cases"])).context["form"]
        self.assertNotIn("module", form.fields)
        self.assertEqual(form.initial["rubric"], self.rubric.pk)

        response = self.client.post(reverse("manage:crud_create", args=["visual_cases"]), {
            "title": "Yangi vizual keys", "body": "Tasvirni tahlil qiling", "component": "COG", "bloom_level": 4,
            "rubric": self.rubric.pk, "estimated_minutes": 20, "difficulty": 2, "is_active": "on",
        })
        self.assertEqual(response.status_code, 302)
        case = Assignment.objects.get(title="Yangi vizual keys")
        self.assertEqual((case.module, case.kind), (Module.VISUAL, Assignment.Kind.VISUAL))
        self.assertIn(reverse("manage:crud_edit", args=["visual_cases", case.pk]),
                      self.client.get(reverse("assignments:cases")).content.decode())

    def test_practice_tasks_limit_modules(self):
        form = self.client.get(reverse("manage:crud_create", args=["practice_tasks"]) + "?module=RAQAMLI").context["form"]
        modules = {value for value, _ in form.fields["module"].choices if value}
        self.assertEqual(modules, {Module.LAB, Module.TEACHER, Module.DIGITAL, Module.CREATIVE})
        self.assertEqual(form.initial["module"], "RAQAMLI")
        self.assertEqual(form.initial["kind"], Assignment.Kind.DIGITAL)
        # Vizual keys bu bo'limda tahrirlanmaydi.
        case = Assignment.objects.filter(module=Module.VISUAL).first()
        if case:
            self.assertEqual(self.client.get(reverse("manage:crud_edit", args=["practice_tasks", case.pk])).status_code, 404)

    def _tmp(self):
        import tempfile

        path = tempfile.mkdtemp()
        self.addCleanup(__import__("shutil").rmtree, path, True)
        return path
