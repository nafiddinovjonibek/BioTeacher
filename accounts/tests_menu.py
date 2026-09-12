"""Yon panel menyusi: to'rt blok tuzilmasi, faol band va admin drag & drop sozlamalari."""

import json
import re
from html import unescape

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.enums import Module, Role

User = get_user_model()

BLOCKS = [
    "1-blok: Tadqiqot va eksperiment monitoringi",
    "2-blok: Mustaqil bilim olish",
    "3-blok: O‘z-o‘zini rivojlantirish",
    "4-blok: Refleksiya va o‘z-o‘zini baholash",
]


def rail_nav(html):
    """Birinchi (kompyuter) rail'ning menyu qismi. Allaqachon kesilgan matnni ham qabul qiladi."""
    end = html.find("</nav>")
    return html[html.index('aria-label="Asosiy menyu"'):end if end != -1 else None]


def rail_group(html, code):
    """Bitta guruh (blok) bo'lagi — keyingi guruhgacha."""
    nav = rail_nav(html)
    start = nav.index(f'data-rail-group="{code}"')
    end = nav.find("data-rail-group=", start + 1)
    return nav[start:end if end != -1 else None]


def rail_heading(html, code):
    """Guruh sarlavhasi: (blok yorlig'i, nom) yoki sarlavha yashirilgan bo'lsa None."""
    match = re.search(r'<p class="[^"]*">\s*(?:<span[^>]*>([^<]*)</span>)?([^<]*)</p>', rail_group(html, code))
    return (match.group(1) or "", unescape(match.group(2).strip())) if match else None


def rail_labels(html, code):
    """Guruh ichidagi bandlar yorliqlari (ichma-ich ro'yxat bolalari bilan)."""
    found = re.findall(r'<span class="rail-label[^"]*">([^<]+)</span>', rail_group(html, code))
    return [unescape(label) for label in found]


def active_labels(html):
    """Rail'da aria-current="page" belgilangan bandlar."""
    found = re.findall(r'aria-current="page"[^>]*>.*?class="rail-label[^"]*">([^<]+)<', rail_nav(html), re.S)
    return [unescape(label) for label in found]


class TeacherRailStructureTests(TestCase):
    """O'qituvchi menyusi — metodikaning to'rt bloki, «Fanlar» ichma-ich ro'yxat."""

    def setUp(self):
        from content.models import Section

        self.teacher = User.objects.create_user("rail-blok@test.uz", "parol12345")
        self.teacher.profile.onboarding_done = True
        self.teacher.profile.save()
        self.client.force_login(self.teacher)
        Section.objects.create(title="Biologiya", slug="biologiya", order=0)
        Section.objects.create(title="Genetika", slug="genetika", order=1)

    def test_four_blocks_with_their_items(self):
        html = self.client.get(reverse("home:dashboard")).content.decode()
        self.assertEqual(re.findall(r'data-rail-group="([^"]+)"', rail_nav(html)),
                         ["research", "learning", "development", "reflection"])
        # «N-blok» — alohida yorqin yorliq, qolgani — blok nomi.
        self.assertEqual(
            [rail_heading(html, code) for code in ["research", "learning", "development", "reflection"]],
            [("1-blok", "Tadqiqot va eksperiment monitoringi"), ("2-blok", "Mustaqil bilim olish"),
             ("3-blok", "O‘z-o‘zini rivojlantirish"), ("4-blok", "Refleksiya va o‘z-o‘zini baholash")],
        )
        self.assertEqual(rail_labels(html, "research"), ["Bosh sahifa", "Test", "Statistika", "Maqsadlarim"])
        self.assertEqual(rail_labels(html, "learning"), ["Fanlar", "Biologiya", "Genetika", "Mavzular", "AI-sokratik"])
        self.assertEqual(rail_labels(html, "development"), [
            "Muammoli vizual keyslar", "3D simulyatsiyalar",
            "Virtual laboratoriya va amaliy topshiriqlar", "Maktab o‘quv-tajriba uchastkasi resurslari",
        ])
        self.assertEqual(rail_labels(html, "reflection"),
                         ["Refleksiya kundaligi", "Kuzatuv varaqasi", "Mening natijalarim"])
        self.assertIn("mustaqil tahlil qilish", rail_nav(html))
        self.assertIn("MOT · ACT · REF · CRE", rail_nav(html))

    def test_every_menu_link_opens(self):
        html = self.client.get(reverse("home:dashboard")).content.decode()
        links = re.findall(r'href="([^"]+)"', rail_nav(html))
        self.assertGreaterEqual(len(links), 15)
        for href in links:
            with self.subTest(href=href):
                self.assertEqual(self.client.get(href).status_code, 200)

    def test_subjects_tree_opens_on_subject_page(self):
        html = self.client.get(reverse("content:section", args=["genetika"])).content.decode()
        self.assertIn('data-rail-tree="bt_tree_learning_subjects" open', rail_nav(html))
        self.assertEqual(active_labels(html), ["Genetika"])

    def test_subjects_tree_closed_by_default_and_remembers_state(self):
        opened = 'data-rail-tree="bt_tree_learning_subjects" open'
        self.assertNotIn(opened, rail_nav(self.client.get(reverse("home:dashboard")).content.decode()))

        self.client.cookies["bt_tree_learning_subjects"] = "1"
        self.assertIn(opened, rail_nav(self.client.get(reverse("home:dashboard")).content.decode()))

        # Fan sahifasida cookie'dan qat'i nazar ochiq.
        self.client.cookies["bt_tree_learning_subjects"] = "0"
        html = self.client.get(reverse("content:section", args=["biologiya"])).content.decode()
        self.assertIn(opened, rail_nav(html))

    def test_single_active_item_on_nested_pages(self):
        cases = [
            (reverse("home:dashboard"), "Bosh sahifa"),
            (reverse("goals:create"), "Maqsadlarim"),
            (reverse("progress:observation"), "Kuzatuv varaqasi"),
            (reverse("progress:monitoring"), "Statistika"),
            # Boshqa amaliy modullar ham shu band ostida.
            (reverse("assignments:module", args=[Module.CREATIVE]), "Virtual laboratoriya va amaliy topshiriqlar"),
            (reverse("home:upcoming", args=["ai-sokratik"]), "AI-sokratik"),
        ]
        for url, label in cases:
            with self.subTest(url=url):
                self.assertEqual(active_labels(self.client.get(url).content.decode()), [label])

    def test_upcoming_unknown_slug_is_404(self):
        self.assertEqual(self.client.get(reverse("home:upcoming", args=["yoq"])).status_code, 404)

    def test_practice_modules_are_tabs_under_lab_item(self):
        html = self.client.get(reverse("assignments:module", args=[Module.TEACHER])).content.decode()
        tabs = html[html.index('aria-label="Amaliy topshiriqlar bo‘limlari"'):]
        tabs = tabs[:tabs.index("</nav>")]
        labels = re.findall(r'</span>\s*([^<]+?)\s*</a>', tabs)
        self.assertEqual(labels, ["Laboratoriya", "Men — o‘qituvchi", "Raqamli biologiya", "Kreativ o‘qituvchi"])
        current = re.findall(r'aria-current="page".*?</span>\s*([^<]+?)\s*</a>', tabs, re.S)
        self.assertEqual(current, ["Men — o‘qituvchi"])


class MenuOrderTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("menu-admin@test.uz", "parol12345")
        self.admin.profile.set_roles([Role.TEACHER, Role.ADMIN], active=Role.ADMIN)
        self.admin.profile.onboarding_done = True
        self.admin.profile.save()
        self.client.force_login(self.admin)

    def _post(self, group, keys):
        return self.client.post(reverse("manage:menu_reorder"), json.dumps({"group": group, "keys": keys}),
                                content_type="application/json")

    def test_menu_page_lists_all_groups(self):
        response = self.client.get(reverse("manage:menu"))
        self.assertEqual(response.status_code, 200)
        for text in [*BLOCKS, "Boshqaruv", "«Fanlar» ichidagi ro‘yxat", "Kuzatuv varaqasi", "Menyu tartibi"]:
            self.assertContains(response, text)

    def test_reorder_changes_teacher_rail(self):
        response = self._post("development", ["development.plot", "development.cases"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["keys"][:2], ["development.plot", "development.cases"])
        self.assertEqual(len(response.json()["keys"]), 4)  # qolganlari oxiriga qo'shildi

        self.client.post(reverse("accounts:switch_role"), {"role": Role.TEACHER})
        html = self.client.get(reverse("home:cabinet")).content.decode()
        labels = rail_labels(html, "development")
        self.assertEqual(labels[:2], ["Maktab o‘quv-tajriba uchastkasi resurslari", "Muammoli vizual keyslar"])

    def test_reorder_admin_menu_and_reset(self):
        self._post("admin", ["admin.export", "admin.students"])
        html = self.client.get(reverse("home:cabinet")).content.decode()
        self.assertEqual(rail_heading(html, "admin"), ("", "Boshqaruv"))  # blok raqamisiz sarlavha
        self.assertEqual(rail_labels(html, "admin")[:2], ["Eksport", "O‘qituvchilar"])

        self.client.post(reverse("manage:menu_reset", args=["admin"]))
        html = self.client.get(reverse("home:cabinet")).content.decode()
        self.assertEqual(rail_labels(html, "admin")[0], "O‘qituvchilar")

    def test_admin_rail_marks_subpage_parent(self):
        html = self.client.get(reverse("manage:crud_list", args=["sections"])).content.decode()
        self.assertEqual(active_labels(html), ["Ma'lumotlar (CRUD)"])

    def test_invalid_input(self):
        self.assertEqual(self._post("yoq", []).status_code, 400)
        self.assertEqual(self._post("sections", []).status_code, 400)  # endi guruh emas
        self.assertEqual(self.client.get(reverse("manage:menu_reorder")).status_code, 405)
        response = self._post("reflection", ["begona.kalit", "reflection.results"])
        self.assertEqual(response.json()["keys"][0], "reflection.results")
        self.assertNotIn("begona.kalit", response.json()["keys"])

    def test_teacher_cannot_reorder(self):
        self.client.post(reverse("accounts:switch_role"), {"role": Role.TEACHER})
        self.assertEqual(self.client.get(reverse("manage:menu")).status_code, 403)
        self.assertEqual(self._post("research", ["research.goals"]).status_code, 403)


class MenuRenameAndGroupOrderTests(TestCase):
    """Band/guruh nomini o'zgartirish va kartalar (guruhlar) tartibi."""

    def setUp(self):
        self.admin = User.objects.create_user("menu-admin2@test.uz", "parol12345")
        self.admin.profile.set_roles([Role.TEACHER, Role.ADMIN], active=Role.ADMIN)
        self.admin.profile.onboarding_done = True
        self.admin.profile.save()
        self.client.force_login(self.admin)

    def _json(self, name, payload):
        return self.client.post(reverse(name), json.dumps(payload), content_type="application/json")

    def _teacher_rail(self):
        self.client.post(reverse("accounts:switch_role"), {"role": Role.TEACHER})
        html = self.client.get(reverse("home:cabinet")).content.decode()
        self.client.post(reverse("accounts:switch_role"), {"role": Role.ADMIN})
        return rail_nav(html)

    def test_rename_item_and_back_to_default(self):
        r = self._json("manage:menu_rename", {"kind": "item", "key": "research.tests", "label": "  Testlar  "})
        self.assertEqual(r.json(), {"ok": True, "label": "Testlar"})
        self.assertIn(">Testlar<", self._teacher_rail())
        self.assertContains(self.client.get(reverse("manage:menu")), "o'zgartirilgan")

        r = self._json("manage:menu_rename", {"kind": "item", "key": "research.tests", "label": ""})
        self.assertEqual(r.json()["label"], "Test")
        self.assertIn(">Test<", self._teacher_rail())

    def test_rename_group_and_hide_title(self):
        self._json("manage:menu_rename", {"kind": "group", "key": "development", "label": "O'sish"})
        self.assertEqual(rail_heading(self._teacher_rail(), "development"), ("", "O'sish"))
        self._json("manage:menu_rename", {"kind": "group", "key": "development", "label": "5-BLOK. Yangi nom"})
        self.assertEqual(rail_heading(self._teacher_rail(), "development"), ("5-BLOK", "Yangi nom"))

        self._json("manage:menu_rename", {"kind": "group", "key": "development", "label": ""})
        rail = self._teacher_rail()
        self.assertIsNone(rail_heading(rail, "development"))
        self.assertIn(">3D simulyatsiyalar<", rail)  # bandlar joyida

        self.client.post(reverse("manage:menu_reset", args=["development"]))
        self.assertEqual(rail_heading(self._teacher_rail(), "development"), ("3-blok", "O‘z-o‘zini rivojlantirish"))

    def test_rename_section_changes_subject_title(self):
        from content.models import Section

        section = Section.objects.create(title="Botanika", slug="botanika")
        r = self._json("manage:menu_rename", {"kind": "section", "key": str(section.pk), "label": "O'simliklar"})
        self.assertTrue(r.json()["ok"])
        section.refresh_from_db()
        self.assertEqual(section.title, "O'simliklar")
        self.assertEqual(section.slug, "botanika")  # havola buzilmaydi
        self.assertEqual(self._json("manage:menu_rename", {"kind": "section", "key": str(section.pk), "label": " "}).status_code, 400)

    def test_group_order_changes_rail(self):
        from content.models import Section

        Section.objects.create(title="Genetika", slug="genetika")
        r = self._json("manage:menu_reorder", {"group": "__groups__", "keys": ["reflection", "learning"]})
        self.assertEqual(r.json()["keys"], ["reflection", "learning", "research", "development"])
        rail = self._teacher_rail()
        self.assertLess(rail.index("Kuzatuv varaqasi"), rail.index("Genetika"))
        self.assertLess(rail.index("Genetika"), rail.index("Bosh sahifa"))

        self.client.post(reverse("manage:menu_reset", args=["groups"]))
        rail = self._teacher_rail()
        self.assertLess(rail.index("Bosh sahifa"), rail.index("Genetika"))

    def test_subjects_item_hidden_without_sections(self):
        rail = self._teacher_rail()
        self.assertNotIn(">Fanlar<", rail)
        self.assertIn(">Mavzular<", rail)

    def test_invalid_rename(self):
        self.assertEqual(self._json("manage:menu_rename", {"kind": "item", "key": "yoq", "label": "x"}).status_code, 400)
        self.assertEqual(self._json("manage:menu_rename", {"kind": "group", "key": "sections", "label": "x"}).status_code, 400)
        self.assertEqual(self.client.get(reverse("manage:menu_rename")).status_code, 405)


class MenuEditingTests(TestCase):
    """Blok, band va ichki bandni qo'shish, tahrirlash, ko'chirish va o'chirish."""

    def setUp(self):
        self.admin = User.objects.create_user("menu-edit@test.uz", "parol12345")
        self.admin.profile.set_roles([Role.TEACHER, Role.ADMIN], active=Role.ADMIN)
        self.admin.profile.onboarding_done = True
        self.admin.profile.save()
        self.client.force_login(self.admin)

    def _teacher_rail(self, url=None):
        self.client.post(reverse("accounts:switch_role"), {"role": Role.TEACHER})
        html = self.client.get(url or reverse("home:cabinet")).content.decode()
        self.client.post(reverse("accounts:switch_role"), {"role": Role.ADMIN})
        return rail_nav(html)

    def _save(self, **data):
        return self.client.post(reverse("manage:menu_item_save"), data, follow=True)

    def _item(self, **lookup):
        from accounts.models import MenuItem

        return MenuItem.objects.get(**lookup)

    def test_add_block_item_and_sub_item_then_delete(self):
        from accounts.models import MenuGroup, MenuItem

        self.client.post(reverse("manage:menu_group_add"), {"title": "5-blok: Loyiha ishlari"})
        group = MenuGroup.objects.get(title="5-blok: Loyiha ishlari")
        self.assertEqual(group.audience, "teacher")

        self._save(group=group.key, page="inbox")
        parent = self._item(group=group, parent__isnull=True)
        self._save(group=group.key, parent=parent.key, page="", url="https://example.org/lab", label="Tashqi lab")
        self._save(group=group.key, parent=parent.key, page="competency", label="Mening checklistim", icon="spark")

        rail = self._teacher_rail()
        self.assertEqual(rail_heading(rail, group.key), ("5-blok", "Loyiha ishlari"))
        self.assertEqual(rail_labels(rail, group.key), ["Xabarlar", "Tashqi lab", "Mening checklistim"])
        self.assertRegex(rail, r'href="https://example\.org/lab"\s+target="_blank" rel="noopener"')

        # Ichki band sahifasida — o'zi faol, ota ro'yxat ochiq.
        rail = self._teacher_rail(reverse("assignments:competency"))
        self.assertEqual(active_labels(rail), ["Mening checklistim"])
        self.assertIn(f'data-rail-tree="bt_tree_{parent.key}" open', rail)

        child = self._item(label="Tashqi lab")
        self.client.post(reverse("manage:menu_item_delete", args=[child.key]))
        self.assertNotIn("Tashqi lab", self._teacher_rail())

        self.client.post(reverse("manage:menu_item_delete", args=[parent.key]))
        self.assertFalse(MenuItem.objects.filter(group=group).exists())  # ichki bandlar ham o'chdi

        self.client.post(reverse("manage:menu_group_delete", args=[group.key]))
        self.assertFalse(MenuGroup.objects.filter(key=group.key).exists())

    def test_edit_item_changes_target_icon_and_hint(self):
        item = self._item(key="research.tests")
        self._save(key=item.key, page="", url="/biobilim/", label="Bilim bazasi", icon="book", hint="yangi")
        item.refresh_from_db()
        self.assertEqual((item.page, item.url, item.label, item.icon, item.hint),
                         ("", "/biobilim/", "Bilim bazasi", "book", "yangi"))
        self.assertIn('href="/biobilim/"', rail_group(self._teacher_rail(), "research"))

        # Standart nomni qayta yozish — «standart» sifatida saqlanadi.
        self._save(key=item.key, page="tests", label="Test")
        item.refresh_from_db()
        self.assertEqual((item.page, item.url, item.label), ("tests", "", ""))

    def test_validation_errors(self):
        cases = [
            ({"group": "research", "page": "", "url": "javascript:alert(1)", "label": "X"}, "Havola"),
            ({"group": "research", "page": "", "url": "//evil.example", "label": "X"}, "Havola"),
            ({"group": "research", "page": "", "url": "", "label": "X"}, "Sahifani tanlang"),
            ({"group": "research", "page": "", "url": "/x/"}, "nom yozing"),
            ({"group": "research", "page": "admin.export"}, "qo‘shib bo‘lmaydi"),
            ({"group": "admin", "page": "goals"}, "qo‘shib bo‘lmaydi"),
            ({"group": "research", "page": "yoq"}, "qo‘shib bo‘lmaydi"),
            ({"group": "research", "parent": "research.home", "page": "sections"}, "ichki band bo‘la olmaydi"),
            ({"group": "yoq", "page": "goals"}, "Blok topilmadi"),
        ]
        for data, error in cases:
            with self.subTest(data=data):
                self.assertContains(self._save(**data), error)

        # Ikki qavatdan chuqur emas: ichki bandning ichiga band qo'shilmaydi.
        self._save(group="research", parent="research.home", page="goals")
        child = self._item(parent__key="research.home")
        self.assertContains(self._save(group="research", parent=child.key, page="tests"), "ikki qavatdan")

    def test_locked_admin_parts_cannot_be_removed_or_redirected(self):
        from accounts.models import MenuGroup

        self.assertContains(self.client.post(reverse("manage:menu_item_delete", args=["admin.menu"]), follow=True),
                            "o‘chirib bo‘lmaydi")
        self.assertContains(self.client.post(reverse("manage:menu_group_delete", args=["admin"]), follow=True),
                            "o‘chirib bo‘lmaydi")
        self.assertTrue(MenuGroup.objects.filter(key="admin").exists())

        self._save(key="admin.menu", page="admin.export", label="Menyu")
        item = self._item(key="admin.menu")
        self.assertEqual((item.page, item.label), ("admin.menu", "Menyu"))

    def test_drag_item_to_another_block_moves_it_with_children(self):
        self._save(group="learning", parent="learning.topics", page="goals")
        response = self.client.post(
            reverse("manage:menu_reorder"),
            json.dumps({"group": "research", "keys": ["research.home", "learning.topics"]}),
            content_type="application/json",
        )
        self.assertEqual(response.json()["keys"][:2], ["research.home", "learning.topics"])
        topics = self._item(key="learning.topics")
        self.assertEqual(topics.group.key, "research")
        self.assertEqual(topics.children.get().group.key, "research")

        # Admin menyusiga o'qituvchi bandi o'tmaydi.
        self.client.post(reverse("manage:menu_reorder"), json.dumps({"group": "admin", "keys": ["research.home"]}),
                         content_type="application/json")
        self.assertEqual(self._item(key="research.home").group.key, "research")

    def test_children_reorder(self):
        for page in ["goals", "tests", "stats"]:
            self._save(group="research", parent="research.home", page=page)
        keys = list(self._item(key="research.home").children.values_list("key", flat=True))
        response = self.client.post(reverse("manage:menu_reorder"),
                                    json.dumps({"parent": "research.home", "keys": keys[::-1]}),
                                    content_type="application/json")
        self.assertEqual(response.json()["keys"], keys[::-1])
        self.assertEqual(rail_labels(self._teacher_rail(), "research")[:4],
                         ["Bosh sahifa", "Statistika", "Test", "Maqsadlarim"])

    def test_reset_block_and_whole_menu(self):
        from accounts.models import MenuGroup

        self.client.post(reverse("manage:menu_item_delete", args=["development.sim3d"]))
        self._save(group="development", page="inbox")
        self.client.post(reverse("manage:menu_reset", args=["development"]))
        self.assertEqual(rail_labels(self._teacher_rail(), "development"), [
            "Muammoli vizual keyslar", "3D simulyatsiyalar",
            "Virtual laboratoriya va amaliy topshiriqlar", "Maktab o‘quv-tajriba uchastkasi resurslari",
        ])

        self.client.post(reverse("manage:menu_group_add"), {"title": "Qo'shimcha"})
        self.client.post(reverse("manage:menu_group_delete", args=["reflection"]))
        self.client.post(reverse("manage:menu_reset", args=["all"]))
        self.assertEqual(list(MenuGroup.objects.filter(audience="teacher").values_list("key", flat=True)),
                         ["research", "learning", "development", "reflection"])

    def test_menu_page_has_editor_and_teacher_is_blocked(self):
        response = self.client.get(reverse("manage:menu"))
        self.assertContains(response, 'id="item-dialog"')
        self.assertContains(response, 'id="menu-data"')
        self.assertContains(response, "Blok qo‘shish")

        self.assertEqual(self.client.get(reverse("manage:menu_item_save")).status_code, 405)
        self.client.post(reverse("accounts:switch_role"), {"role": Role.TEACHER})
        for name, args in [("manage:menu_group_add", []), ("manage:menu_group_delete", ["research"]),
                           ("manage:menu_item_save", []), ("manage:menu_item_delete", ["research.home"])]:
            with self.subTest(name=name):
                self.assertEqual(self.client.post(reverse(name, args=args), {"group": "research", "page": "goals"}).status_code, 403)
        self.assertEqual(self._item(key="research.home").group.key, "research")

    def test_link_item_needs_a_name_on_rename(self):
        self._save(group="research", page="", url="/biobilim/", label="Bilim")
        item = self._item(url="/biobilim/")
        response = self.client.post(reverse("manage:menu_rename"),
                                    json.dumps({"kind": "item", "key": item.key, "label": " "}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 400)
