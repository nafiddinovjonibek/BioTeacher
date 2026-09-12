"""
Yon panel (rail) menyusi — to'liq bazada: `MenuGroup` (blok) → `MenuItem` (band) → ichki band.

Admin «Menyu tartibi» sahifasida bloklar, bandlar va ichki bandlarni qo'shadi,
o'chiradi, nomini o'zgartiradi va tortib joyini almashtiradi. Kodda faqat ikki narsa:
• PAGES — band ulanishi mumkin bo'lgan ichki sahifalar (URL, standart nom, ikonka);
• DEFAULT_MENU — standart menyu. Migratsiya bazani shu bilan to'ldiradi,
  «Standart holatga qaytarish» ham shu holatni tiklaydi.
"""

import re
import uuid
from collections import defaultdict

from django.db.models import F, Max
from django.urls import reverse

TEACHER, ADMIN = "teacher", "admin"
LABEL_MAX = 60

# «1-blok: Nom» ko'rinishidagi sarlavhada blok raqami menyuda alohida yorliq bo'lib chiqadi.
BLOCK_PREFIX = re.compile(r"^\s*(\d+\s*-\s*blok)\b\s*[:.]?\s*(?=\S)", re.IGNORECASE)

# Ichma-ich ro'yxat holati shu cookie'da (JS yozadi) — sahifa server tomonda
# to'g'ri holatda chiziladi va ochilib-yopilib "sakramaydi".
TREE_COOKIE = "bt_tree_{}"

# Fan slugiga mos ikonka. Yangi fan qo'shilsa shu yerga bitta qator.
SECTION_ICONS = {
    "hujayra-biologiyasi": "microscope",
    "genetika": "dna",
    "ekologiya": "globe",
    "metodika": "users",
    "zoologiya": "paw",
    "botanika": "leaf",
    "anatomiya": "user",
    "mikrobiologiya": "atom",
}

SECTION_PREFIX = "section:"   # page = "section:<slug>" — bitta fan sahifasi
SECTIONS_PAGE = "sections"    # page = "sections" — barcha fanlar ichma-ich ro'yxat bo'lib

# Band ulanishi mumkin bo'lgan sahifalar. Ixtiyoriy maydonlar: `arg` — URL argumenti;
# `hint` — yangi bandning standart izohi; `ns` — shu namespace'dagi boshqa sahifalarda
# ham band faol; `badge` — hisoblagich; `audience` — kimning menyusi (standart — o'qituvchi).
PAGES = {
    "dashboard": {"url": "home:dashboard", "label": "Bosh sahifa", "icon": "home"},
    "tests": {"url": "diagnostics:index", "label": "Test", "icon": "clipboard"},
    "stats": {"url": "progress:monitoring", "label": "Statistika", "icon": "chart"},
    "goals": {"url": "goals:list", "label": "Maqsadlarim", "icon": "target"},
    SECTIONS_PAGE: {"label": "Fanlar", "icon": "library"},
    "topics": {"url": "content:index", "label": "Mavzular", "icon": "book"},
    "socratic": {"url": "home:upcoming", "arg": "ai-sokratik", "label": "AI-sokratik", "icon": "bot"},
    "cases": {"url": "assignments:cases", "label": "Muammoli vizual keyslar", "icon": "image",
              "hint": "mustaqil tahlil qilish"},
    "sim3d": {"url": "home:upcoming", "arg": "3d-simulyatsiyalar", "label": "3D simulyatsiyalar", "icon": "box"},
    # Boshqa amaliy modullar (pedagog, raqamli, kreativ) shu sahifadagi yorliqlarda ham bor.
    "lab": {"url": "assignments:module", "arg": "LAB", "label": "Virtual laboratoriya va amaliy topshiriqlar",
            "icon": "microscope", "ns": "assignments"},
    "pedagog": {"url": "assignments:module", "arg": "PEDAGOG", "label": "Men — o‘qituvchi", "icon": "users"},
    "digital": {"url": "assignments:module", "arg": "RAQAMLI", "label": "Raqamli biologiya", "icon": "globe"},
    "creative": {"url": "assignments:module", "arg": "KREATIV", "label": "Kreativ o‘qituvchi", "icon": "spark"},
    "gallery": {"url": "assignments:gallery", "label": "Ijodiy galereya", "icon": "image"},
    "competency": {"url": "assignments:competency", "label": "Kompetensiya checklisti", "icon": "check"},
    "plot": {"url": "home:upcoming", "arg": "tajriba-uchastkasi", "label": "Maktab o‘quv-tajriba uchastkasi resurslari",
             "icon": "sprout"},
    "journal": {"url": "reflection:journal", "label": "Refleksiya kundaligi", "icon": "pen"},
    "observation": {"url": "progress:observation", "label": "Kuzatuv varaqasi", "icon": "eye",
                    "hint": "MOT · ACT · REF · CRE"},
    "results": {"url": "gamification:achievements", "label": "Mening natijalarim", "icon": "trophy"},
    "inbox": {"url": "notifications:inbox", "label": "Xabarlar", "icon": "bell", "badge": "unread_notifications"},
    "cabinet": {"url": "home:cabinet", "label": "Shaxsiy kabinet", "icon": "user"},
    # --- admin
    "admin.students": {"url": "manage:students", "label": "O‘qituvchilar", "icon": "users", "audience": ADMIN},
    "admin.analytics": {"url": "manage:analytics", "label": "Analitika", "icon": "chart", "audience": ADMIN},
    "admin.announce": {"url": "manage:announce", "label": "E’lon yuborish", "icon": "send", "audience": ADMIN},
    "admin.crud": {"url": "manage:crud_index", "label": "Ma'lumotlar (CRUD)", "icon": "shield", "audience": ADMIN},
    "admin.menu": {"url": "manage:menu", "label": "Menyu tartibi", "icon": "menu", "audience": ADMIN},
    "admin.queue": {"url": "assignments:queue", "label": "Tekshirish navbati", "icon": "inbox",
                    "badge": "review_count", "audience": ADMIN},
    "admin.research": {"url": "research:dashboard", "label": "Tadqiqot paneli", "icon": "flask", "audience": ADMIN},
    "admin.statistics": {"url": "research:statistics", "label": "Statistika", "icon": "chart", "audience": ADMIN},
    "admin.export": {"url": "research:export", "label": "Eksport", "icon": "download", "audience": ADMIN},
}

# Band uchun ikonka tanlovi (partials/icon.html nomlari).
ICONS = [
    "home", "clipboard", "chart", "target", "library", "book", "bot", "image", "box", "microscope",
    "sprout", "leaf", "flask", "dna", "atom", "globe", "paw", "pen", "eye", "trophy", "spark",
    "users", "user", "calendar", "bell", "inbox", "send", "download", "shield", "check", "link", "menu",
]

# Standart menyu: blok → bandlar (kalit, sahifa). Kalitlar barqaror — o'zgartirmang.
DEFAULT_MENU = [
    {"key": "research", "title": "1-blok: Tadqiqot va eksperiment monitoringi", "audience": TEACHER, "items": [
        ("research.home", "dashboard"), ("research.tests", "tests"),
        ("research.stats", "stats"), ("research.goals", "goals"),
    ]},
    {"key": "learning", "title": "2-blok: Mustaqil bilim olish", "audience": TEACHER, "items": [
        ("learning.subjects", SECTIONS_PAGE), ("learning.topics", "topics"), ("learning.socratic", "socratic"),
    ]},
    {"key": "development", "title": "3-blok: O‘z-o‘zini rivojlantirish", "audience": TEACHER, "items": [
        ("development.cases", "cases"), ("development.sim3d", "sim3d"),
        ("development.lab", "lab"), ("development.plot", "plot"),
    ]},
    {"key": "reflection", "title": "4-blok: Refleksiya va o‘z-o‘zini baholash", "audience": TEACHER, "items": [
        ("reflection.journal", "journal"), ("reflection.observation", "observation"),
        ("reflection.results", "results"),
    ]},
    {"key": "admin", "title": "Boshqaruv", "audience": ADMIN, "items": [
        ("admin.students", "admin.students"), ("admin.analytics", "admin.analytics"),
        ("admin.crud", "admin.crud"), ("admin.menu", "admin.menu"), ("admin.queue", "admin.queue"),
        ("admin.research", "admin.research"), ("admin.statistics", "admin.statistics"),
        ("admin.export", "admin.export"),
    ]},
]
DEFAULT_GROUPS = {spec["key"]: spec for spec in DEFAULT_MENU}

# O'chirib bo'lmaydi: admin menyusi va «Menyu tartibi» bandi — aks holda bu sahifaga yo'l yo'qoladi.
LOCKED_GROUPS = {"admin"}
LOCKED_ITEMS = {"admin.menu"}


# ------------------------------------------------------------------ sahifalar

def page_audience(page):
    if page.startswith(SECTION_PREFIX):
        return TEACHER
    return PAGES[page].get("audience", TEACHER) if page in PAGES else None


def active_sections():
    """Faol fanlar — yon paneldagi ikonka bilan (`icon_name`)."""
    from content.models import Section

    sections = list(Section.objects.filter(is_active=True).order_by("order", "title"))
    for section in sections:
        section.icon_name = SECTION_ICONS.get(section.slug, "leaf")
    return sections


def page_choices(audience, sections=()):
    """Sahifa tanlovi: [(guruh nomi, [(qiymat, nom), ...]), ...]."""
    pages = [(key, page["label"]) for key, page in PAGES.items() if page.get("audience", TEACHER) == audience]
    pages = [(k, "Fanlar ro‘yxati (avtomatik)" if k == SECTIONS_PAGE else label) for k, label in pages]
    choices = [("Sahifalar", pages)]
    if audience == TEACHER and sections:
        choices.append(("Fanlar", [(SECTION_PREFIX + s.slug, s.title) for s in sections]))
    return choices


def _resolve(item, sections):
    """Band manzili: {"href", "label", "icon", "page", "slug"} yoki None — sahifa endi yo'q bo'lsa."""
    if item.page.startswith(SECTION_PREFIX):
        section = sections.get(item.page[len(SECTION_PREFIX):])
        if section is None:
            return None
        return {"href": reverse("content:section", args=[section.slug]), "label": section.title,
                "icon": section.icon_name, "page": {}, "slug": section.slug}
    if item.page:
        page = PAGES.get(item.page)
        if page is None:
            return None
        href = reverse(page["url"], args=[page["arg"]] if page.get("arg") else None) if page.get("url") else ""
        return {"href": href, "label": page["label"], "icon": page["icon"], "page": page, "slug": None}
    if item.url:
        return {"href": item.url, "label": item.url, "icon": "link", "page": {}, "slug": None}
    return None


def is_safe_url(url):
    """Faqat sayt ichidagi yo'l («/…») yoki http(s) havola — `javascript:` va boshqalar emas."""
    if re.search(r'[\s"<>]', url):
        return False
    if url.startswith("/"):
        return not url.startswith("//")
    return re.match(r"^https?://[^/]+", url, re.IGNORECASE) is not None


# ------------------------------------------------------------------ o'qish

def group_title(group):
    """None — standart sarlavha; "" — sarlavha ko'rsatilmaydi."""
    if group.title is not None:
        return group.title
    return DEFAULT_GROUPS.get(group.key, {}).get("title", "")


def _load(audience=None):
    """[(blok, [(band, [ichki band, ...]), ...]), ...] — ikki so'rov bilan."""
    from .models import MenuGroup, MenuItem

    if not MenuGroup.objects.exists():
        # Bo'sh baza (masalan, jadvallar tozalangan) — standart menyu bilan to'ldiriladi.
        seed_defaults(MenuGroup, MenuItem)
    groups = MenuGroup.objects.order_by(F("order").asc(nulls_last=True), "id")
    if audience:
        groups = groups.filter(audience=audience)
    groups = list(groups)
    top, children = defaultdict(list), defaultdict(list)
    for item in MenuItem.objects.filter(group__in=groups).order_by("order", "id"):
        (children[item.parent_id] if item.parent_id else top[item.group_id]).append(item)
    return [(group, [(item, children[item.id]) for item in top[group.id]]) for group in groups]


def _current_section(request):
    """Fan, mavzu yoki dars sahifasida — o'sha fanning slugi."""
    match = getattr(request, "resolver_match", None)
    if match is None or match.namespace != "content":
        return None
    return match.kwargs.get("slug") if match.url_name == "section" else match.kwargs.get("section_slug")


def _mark_active(groups, request):
    """
    Menyuda bitta band faol bo'ladi: view belgilagan sahifa (`request.menu_page`);
    fan/mavzu/dars sahifasida — o'sha fan; aks holda manzili joriy yo'lning eng uzun
    boshlanishi bo'lgan band; u ham topilmasa — `ns` namespace'i mos band.
    Faol band ichki ro'yxatda bo'lsa (yoki o'zida ichki ro'yxat bo'lsa) — ro'yxat ochiladi.
    """
    if request is None:
        return
    rows = []
    for group in groups:
        for item in group["items"]:
            rows.append((item, None))
            rows += [(child, item) for child in item.get("children", ())]

    def activate(row, parent):
        row["active"] = True
        for tree in (parent, row):
            if tree is not None and tree.get("children"):
                tree["open"] = True

    # View o'zi aytishi mumkin: `request.menu_page = "cases"` — shu sahifaga ulangan band faol.
    page = getattr(request, "menu_page", None)
    found = next(((row, parent) for row, parent in rows if page and row.get("page") == page), None)

    section = _current_section(request)
    if found is None:
        found = next(((row, parent) for row, parent in rows if section and row.get("slug") == section), None)

    if found is None:
        path = request.path
        prefixed = [
            (row, parent) for row, parent in rows
            if row["href"] and not row["external"]
            and (path == row["href"] or (row["href"] != "/" and path.startswith(row["href"])))
        ]
        if prefixed:
            found = max(prefixed, key=lambda rp: len(rp[0]["href"]))

    if found is None:
        match = getattr(request, "resolver_match", None)
        namespace = match.namespace if match else None
        found = next(((row, parent) for row, parent in rows if namespace and row.get("ns") == namespace), None)

    if found is not None:
        activate(*found)


def rail_menu(badges, sections, request=None):
    """
    Context processor uchun:
    {"teacher": [{"code", "title", "badge", "text", "items"}...], "admin": [...]}.
    Har bir bandda tayyor `href` va `active`; ichki ro'yxatli bandda `children` va `open`.
    `sections` — `active_sections()` natijasi.
    """
    by_slug = {s.slug: s for s in sections}
    cookies = getattr(request, "COOKIES", {})

    def row(item):
        target = _resolve(item, by_slug)
        if target is None:
            return None
        page = target["page"]
        return {
            "key": item.key, "label": item.label or target["label"], "icon": item.icon or target["icon"],
            "hint": item.hint, "href": target["href"], "slug": target["slug"], "page": item.page,
            "external": target["href"].startswith(("http://", "https://")),
            "ns": page.get("ns"), "badge": badges.get(page["badge"], 0) if page.get("badge") else 0,
            "active": False,
        }

    def build(group, entries):
        items = []
        for item, kids in entries:
            current = row(item)
            if current is None:
                continue
            children = []
            if item.page == SECTIONS_PAGE:
                children = [
                    {"key": f"{SECTION_PREFIX}{s.slug}", "slug": s.slug, "label": s.title, "icon": s.icon_name,
                     "href": reverse("content:section", args=[s.slug]), "external": False, "active": False}
                    for s in sections
                ]
            children += [child for child in (row(kid) for kid in kids) if child]
            if item.page == SECTIONS_PAGE and not children:
                continue  # fan ham, ichki band ham yo'q — bo'sh ro'yxat ko'rsatilmaydi
            if children:
                current["children"] = children
                current["cookie"] = TREE_COOKIE.format(item.key.replace(".", "_"))
                current["open"] = cookies.get(current["cookie"]) == "1"
            items.append(current)
        title = group_title(group)
        block = BLOCK_PREFIX.match(title)
        return {
            "code": group.key, "title": title, "items": items,
            "badge": block.group(1) if block else "",
            "text": title[block.end():] if block else title,
        }

    menus = {TEACHER: [], ADMIN: []}
    for group, entries in _load():
        built = build(group, entries)
        if built["items"]:
            menus.setdefault(group.audience, []).append(built)
    for groups in menus.values():
        _mark_active(groups, request)
    return {"teacher": menus[TEACHER], "admin": menus[ADMIN]}


def manage_cards(sections):
    """«Menyu tartibi» sahifasi uchun: bloklar, bandlar va ichki bandlar (tahrir ma'lumoti bilan)."""
    by_slug = {s.slug: s for s in sections}

    def row(item):
        target = _resolve(item, by_slug)
        default_label = target["label"] if target and item.page else ""
        if item.page == SECTIONS_PAGE:
            caption = "Fanlar ro‘yxati (avtomatik)"
        elif target is None:
            caption = "Sahifa topilmadi"
        elif item.page.startswith(SECTION_PREFIX):
            caption = f"Fan: {target['label']}"
        elif item.page:
            caption = target["label"]
        else:
            caption = item.url
        return {
            "key": item.key, "label": item.label or default_label, "default_label": default_label,
            "icon": item.icon or (target["icon"] if target else "link"), "caption": caption,
            "external": not item.page, "broken": target is None, "locked": item.key in LOCKED_ITEMS,
            "can_have_children": item.parent_id is None,
            # Tahrirlash oynasi uchun xom qiymatlar.
            "form": {"key": item.key, "label": item.label, "page": item.page, "url": item.url,
                     "icon": item.icon, "hint": item.hint, "locked": item.key in LOCKED_ITEMS},
        }

    cards = []
    for group, entries in _load():
        cards.append({
            "code": group.key, "audience": group.audience, "title": group_title(group),
            "name": DEFAULT_GROUPS.get(group.key, {}).get("title") or "Blok",
            "is_default": group.key in DEFAULT_GROUPS, "locked": group.key in LOCKED_GROUPS,
            "items": [dict(row(item), children=[row(kid) for kid in kids]) for item, kids in entries],
        })
    return cards


def page_defaults(sections):
    """Tahrirlash oynasi uchun: sahifa → standart nom va ikonka (placeholder sifatida)."""
    data = {key: {"label": page["label"], "icon": page["icon"]} for key, page in PAGES.items()}
    data.update({f"{SECTION_PREFIX}{s.slug}": {"label": s.title, "icon": s.icon_name} for s in sections})
    return data


# ------------------------------------------------------------------ yozish

def _new_key(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _next_order(queryset):
    last = queryset.aggregate(last=Max("order"))["last"]
    return 0 if last is None else last + 1


def _default_label(item):
    if item.page.startswith(SECTION_PREFIX):
        from content.models import Section

        section = Section.objects.filter(slug=item.page[len(SECTION_PREFIX):]).first()
        return section.title if section else ""
    return PAGES.get(item.page, {}).get("label", "") if item.page else ""


def add_group(title, audience=TEACHER):
    from .models import MenuGroup

    return MenuGroup.objects.create(
        key=_new_key("blok"), audience=audience,
        title=(title or "").strip()[:LABEL_MAX] or "Yangi blok",
        order=_next_order(MenuGroup.objects.filter(audience=audience)),
    )


def delete_group(code):
    """Blok va uning barcha bandlari. Qulflangan yoki topilmagan blok — False."""
    from .models import MenuGroup

    if code in LOCKED_GROUPS:
        return False
    return bool(MenuGroup.objects.filter(key=code).delete()[0])


def clean_item(data, group, parent, sections):
    """Band formasini tekshiradi. Qaytaradi: (tozalangan dict, None) yoki (None, xato matni)."""
    label = (data.get("label") or "").strip()[:LABEL_MAX]
    page = (data.get("page") or "").strip()
    url = (data.get("url") or "").strip()[:300]
    icon = (data.get("icon") or "").strip()
    hint = (data.get("hint") or "").strip()[:LABEL_MAX]

    if page:
        url = ""
        if page.startswith(SECTION_PREFIX):
            if page[len(SECTION_PREFIX):] not in {s.slug for s in sections}:
                return None, "Bunday fan topilmadi."
        if page_audience(page) != group.audience:
            return None, "Bu sahifani shu menyuga qo‘shib bo‘lmaydi."
        if page == SECTIONS_PAGE and parent is not None:
            return None, "«Fanlar ro‘yxati» ichki band bo‘la olmaydi — u o‘zi ro‘yxat."
    else:
        if not url:
            return None, "Sahifani tanlang yoki havolani yozing."
        if not is_safe_url(url):
            return None, "Havola «/» (sayt ichida) yoki «https://» bilan boshlansin."
        if not label:
            return None, "Havola uchun nom yozing."
    return {"label": label, "page": page, "url": url, "icon": icon if icon in ICONS else "", "hint": hint}, None


def save_item(data, sections, key=None, group_code=None, parent_key=None):
    """
    Band qo'shish (`key` yo'q — `group_code`, ixtiyoriy `parent_key` bilan) yoki tahrirlash.
    Qaytaradi: (band, None) yoki (None, xato matni).
    """
    from .models import MenuGroup, MenuItem

    if key:
        item = MenuItem.objects.select_related("group", "parent").filter(key=key).first()
        if item is None:
            return None, "Band topilmadi."
        group, parent = item.group, item.parent
    else:
        group = MenuGroup.objects.filter(key=group_code).first()
        if group is None:
            return None, "Blok topilmadi."
        parent = None
        if parent_key:
            parent = MenuItem.objects.filter(key=parent_key, group=group, parent__isnull=True).first()
            if parent is None:
                return None, "Ichki band faqat blokning o‘z bandiga qo‘shiladi (ikki qavatdan chuqur emas)."
        siblings = parent.children.all() if parent else group.items.filter(parent__isnull=True)
        item = MenuItem(key=_new_key("band"), group=group, parent=parent, order=_next_order(siblings))

    data = {field: data.get(field) or "" for field in ("label", "page", "url", "icon", "hint")}
    if item.key in LOCKED_ITEMS:  # «Menyu tartibi» doim shu sahifaga olib borsin
        data["page"], data["url"] = item.page, ""
    cleaned, error = clean_item(data, group, parent, sections)
    if error:
        return None, error
    for field, value in cleaned.items():
        setattr(item, field, value)
    if item.page and item.label == _default_label(item):
        item.label = ""
    item.save()
    return item, None


def delete_item(key):
    """Band (ichki bandlari bilan). Qulflangan yoki topilmagan band — False."""
    from .models import MenuItem

    if key in LOCKED_ITEMS:
        return False
    return bool(MenuItem.objects.filter(key=key).delete()[0])


def save_order(group_code, keys):
    """
    Blokdagi bandlar tartibi. Shu menyudagi boshqa blokdan tortib olib kelingan band shu blokka
    ko'chadi (ichki bandlari bilan). Ro'yxatda yo'q bandlar oxiriga qo'shiladi. Blok yo'q — None.
    """
    from .models import MenuGroup, MenuItem

    group = MenuGroup.objects.filter(key=group_code).first()
    if group is None:
        return None
    movable = {i.key: i for i in MenuItem.objects.filter(group__audience=group.audience, parent__isnull=True)}
    keys = [k for k in dict.fromkeys(keys) if k in movable]
    keys += [k for k in group.items.filter(parent__isnull=True).values_list("key", flat=True) if k not in keys]
    for position, key in enumerate(keys):
        item = movable[key]
        if item.group_id != group.id:
            item.children.update(group=group)
        MenuItem.objects.filter(pk=item.pk).update(group=group, order=position)
    return keys


def save_children_order(parent_key, keys):
    """Ichki bandlar tartibi. Ota band topilmasa — None."""
    from .models import MenuItem

    parent = MenuItem.objects.filter(key=parent_key, parent__isnull=True).first()
    if parent is None:
        return None
    existing = list(parent.children.values_list("key", flat=True))
    keys = [k for k in dict.fromkeys(keys) if k in existing]
    keys += [k for k in existing if k not in keys]
    for position, key in enumerate(keys):
        MenuItem.objects.filter(key=key).update(order=position)
    return keys


def save_group_order(codes):
    """O'qituvchi menyusidagi bloklar (kartalar) tartibi."""
    from .models import MenuGroup

    existing = list(
        MenuGroup.objects.filter(audience=TEACHER)
        .order_by(F("order").asc(nulls_last=True), "id").values_list("key", flat=True)
    )
    codes = [c for c in dict.fromkeys(codes) if c in existing]
    codes += [c for c in existing if c not in codes]
    for position, code in enumerate(codes):
        MenuGroup.objects.filter(key=code).update(order=position)
    return codes


def rename_item(key, label):
    """
    Band nomi. Sahifali bandda bo'sh qiymat — standart nomga qaytaradi.
    Qaytaradi: amaldagi nom; band topilmasa yoki havolali band nomsiz qolsa — None.
    """
    from .models import MenuItem

    item = MenuItem.objects.filter(key=key).first()
    if item is None:
        return None
    label = (label or "").strip()[:LABEL_MAX]
    default = _default_label(item)
    if not label and not item.page:
        return None
    item.label = "" if label == default else label
    item.save(update_fields=["label"])
    return item.label or default


def rename_group(code, title):
    """Blok sarlavhasi. Bo'sh — menyuda sarlavha ko'rsatilmaydi. Blok topilmasa — None."""
    from .models import MenuGroup

    group = MenuGroup.objects.filter(key=code).first()
    if group is None:
        return None
    group.title = (title or "").strip()[:LABEL_MAX]
    group.save(update_fields=["title"])
    return group.title


def seed_defaults(MenuGroup, MenuItem, audience=None):
    """
    Standart menyuni bazaga yozadi (yo'q bloklar va bandlar yaratiladi).
    Mavjud yozuvlarning tartibi, nomi va sarlavhasi saqlanadi. Migratsiyadan
    tarixiy modellar bilan ham chaqiriladi, shuning uchun faqat `.objects` ishlatiladi.
    """
    for index, spec in enumerate(DEFAULT_MENU):
        if audience and spec["audience"] != audience:
            continue
        group, created = MenuGroup.objects.get_or_create(
            key=spec["key"], defaults={"order": index, "audience": spec["audience"]},
        )
        if not created:
            group.audience = spec["audience"]
            group.order = index if group.order is None else group.order
            group.save(update_fields=["audience", "order"])
        for position, (key, page) in enumerate(spec["items"]):
            item, created = MenuItem.objects.get_or_create(
                key=key, defaults={"group": group, "order": position, "page": page,
                                   "hint": PAGES[page].get("hint", "")},
            )
            if not created and item.group_id is None:  # eski (katalog davridagi) yozuv
                item.group, item.page, item.hint = group, page, PAGES[page].get("hint", "")
                item.save()


def reset_group(code):
    """
    Standart blokni boshlang'ich holatiga qaytaradi: sarlavha va bandlar
    (qo'shilgan bandlar o'chadi, boshqa blokka ko'chirilgan standart bandlar qaytadi).
    """
    from .models import MenuGroup, MenuItem

    spec = DEFAULT_GROUPS.get(code)
    group = MenuGroup.objects.filter(key=code).first()
    if spec is None or group is None:
        return False
    keys = [key for key, _ in spec["items"]]
    group.items.all().delete()
    MenuItem.objects.filter(key__in=keys).delete()
    for position, (key, page) in enumerate(spec["items"]):
        MenuItem.objects.create(key=key, group=group, order=position, page=page,
                                hint=PAGES[page].get("hint", ""))
    group.title = None
    group.save(update_fields=["title"])
    return True


def reset_group_order():
    """Standart bloklar standart tartibda, qo'shilgan bloklar — ulardan keyin."""
    from .models import MenuGroup

    index = {spec["key"]: i for i, spec in enumerate(DEFAULT_MENU)}
    groups = sorted(MenuGroup.objects.filter(audience=TEACHER), key=lambda g: (index.get(g.key, len(index)), g.id))
    for position, group in enumerate(groups):
        MenuGroup.objects.filter(pk=group.pk).update(order=position)


def reset_all():
    """O'qituvchi menyusini to'liq standart holatga qaytaradi — qo'shilgan bloklar ham o'chadi."""
    from .models import MenuGroup, MenuItem

    MenuGroup.objects.filter(audience=TEACHER).delete()
    teacher_keys = [key for spec in DEFAULT_MENU if spec["audience"] == TEACHER for key, _ in spec["items"]]
    MenuItem.objects.filter(key__in=teacher_keys).delete()  # admin menyusiga ko'chirilgan bo'lsa ham
    seed_defaults(MenuGroup, MenuItem, audience=TEACHER)
