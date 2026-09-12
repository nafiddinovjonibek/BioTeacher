"""
Butun platforma uchun umumiy ilmiy enum'lar va shkalalar.

Manba: TZ.md 2-bo'lim (ilmiy asos va o'lchanadigan model).
Bu yerdagi kodlar bazaga yoziladi — qiymatlarni O'ZGARTIRMANG, faqat qo'shing.
"""

from django.db import models


class Component(models.TextChoices):
    """SR-01 — o'z-o'zini rivojlantirishning 5 komponenti."""

    MOT = "MOT", "Motivatsion-qadriyatli"
    COG = "COG", "Kognitiv"
    ACT = "ACT", "Faoliyatli-texnologik"
    REF = "REF", "Refleksiv"
    CRE = "CRE", "Kreativ"


COMPONENT_ORDER = [Component.MOT, Component.COG, Component.ACT, Component.REF, Component.CRE]

COMPONENT_DESCRIPTIONS = {
    Component.MOT: "Kasbga qiziqish, o'sishga intilish, pedagogik qadriyatlar",
    Component.COG: "Biologik va metodik bilim, tushunish chuqurligi",
    Component.ACT: "Dars loyihalash, metod tanlash va qo'llash ko'nikmasi",
    Component.REF: "O'z faoliyatini tahlil qilish va xulosa chiqarish",
    Component.CRE: "Nostandart pedagogik yechim yarata olish",
}

# SR-04 — standart vaznlar. Yig'indisi 1.00 bo'lishi shart.
DEFAULT_WEIGHTS = {
    Component.MOT.value: 0.15,
    Component.COG.value: 0.25,
    Component.ACT.value: 0.25,
    Component.REF.value: 0.20,
    Component.CRE.value: 0.15,
}


class BloomLevel(models.IntegerChoices):
    """SR-02 — Bloom taksonomiyasi darajalari."""

    KNOW = 1, "Bilaman"
    UNDERSTAND = 2, "Tushunaman"
    APPLY = 3, "Qo'llayman"
    ANALYZE = 4, "Tahlil qilaman"
    EVALUATE = 5, "Baholayman"
    CREATE = 6, "Yarataman"


class Cut(models.TextChoices):
    """SR-06 — tajriba-sinov kesim nuqtalari."""

    INITIAL = "INITIAL", "Boshlang'ich"
    INTERIM_1 = "INTERIM_1", "1-chorak"
    INTERIM_2 = "INTERIM_2", "2-chorak"
    FINAL = "FINAL", "Yakuniy"


CUT_ORDER = [Cut.INITIAL, Cut.INTERIM_1, Cut.INTERIM_2, Cut.FINAL]


class StudyArm(models.TextChoices):
    """Tajriba / nazorat bo'linmasi (FR-04, FR-58)."""

    EXPERIMENTAL = "E", "Tajriba bo'linmasi"
    CONTROL = "C", "Nazorat bo'linmasi"
    NONE = "N", "Tadqiqotdan tashqari"


class Role(models.TextChoices):
    """
    Foydalanuvchi rollari.

    Platforma o'qituvchining o'zini rivojlantirishi uchun: TEACHER — barcha
    bo'limlardan foydalanadi, lekin kontentni o'zgartira olmaydi; ADMIN —
    hamma narsani yaratadi/tahrirlaydi/o'chiradi.
    """

    TEACHER = "TEACHER", "O'qituvchi"
    ADMIN = "ADMIN", "Administrator"


class Module(models.TextChoices):
    """Topshiriq tegishli bo'lgan platforma moduli (TZ 4-bo'lim)."""

    BIOKNOWLEDGE = "BIOBILIM", "BioBilim — kasbiy bilim"
    LAB = "LAB", "Biologik laboratoriya"
    TEACHER = "PEDAGOG", "Men — o'qituvchi"
    DIGITAL = "RAQAMLI", "Raqamli biologiya"
    CREATIVE = "KREATIV", "Kreativ o'qituvchi"
    VISUAL = "VIZUAL", "Muammoli vizual keyslar"


# SR-03 — daraja shkalasi.
#
# MUHIM: shkala qizildan yashilga EMAS, och yashildan toʻq yashilgacha boradi.
# Sabab — SR-07: talaba boshqalar bilan emas, oʻz oldingi natijasi bilan
# taqqoslanadi. Qizil rang "sen yomonsan" degan hukmni bildiradi va bu
# oʻz-oʻzini rivojlantirish metodikasiga zid. Och → toʻq esa "sen shkalaning
# boshidasan" deydi.
#
# Rang yagona kanal EMAS: har bir daraja `step` raqami bilan ham beriladi
# (5 boʻlakli pogʻonali metr), shuning uchun rangni ajrata olmaydigan
# foydalanuvchi ham darajani oʻqiy oladi.
#
# (quyi_chegara, kod, nom, wash_tokeni, pogʻona 1..5)
LEVEL_SCALE = [
    (90, "CREATIVE", "Ijodiy", "scale-5", 5),
    (75, "HIGH", "Yuqori", "scale-4", 4),
    (60, "MEDIUM", "O'rta", "scale-3", 3),
    (40, "LOW_MEDIUM", "Past-o'rta", "scale-2", 2),
    (0, "INITIAL", "Boshlang'ich", "scale-1", 1),
]

LEVEL_STEPS = 5  # pogʻonali metrdagi boʻlaklar soni

LEVEL_HINTS = {
    "CREATIVE": "Namunali daraja — tajribangizni boshqalar bilan bo'lishing.",
    "HIGH": "Yaxshi daraja — ijodiy topshiriqlarga o'ting.",
    "MEDIUM": "Yetarli daraja — muntazamlikni saqlang.",
    "LOW_MEDIUM": "Tizimli ish talab etiladi.",
    "INITIAL": "Rivojlantirish zarur — asosiy modullardan boshlang.",
}


def level_for(percent):
    """
    Foizga mos daraja.

    Qaytaradi: (kod, nom, wash_tokeni, pogʻona_1_5, izoh)
    """
    value = max(0.0, min(100.0, float(percent or 0)))
    for threshold, code, name, wash, step in LEVEL_SCALE:
        if value >= threshold:
            return code, name, wash, step, LEVEL_HINTS[code]
    return "INITIAL", "Boshlang'ich", "scale-1", 1, LEVEL_HINTS["INITIAL"]


def normalize_weights(weights=None):
    """Vaznlarni tekshirib, yig'indisi 1.00 bo'ladigan lug'at qaytaradi (SR-04)."""
    data = dict(DEFAULT_WEIGHTS if weights is None else weights)
    for component in Component.values:
        data.setdefault(component, 0.0)
        data[component] = max(0.0, float(data[component]))
    total = sum(data.values())
    if total <= 0:
        return dict(DEFAULT_WEIGHTS)
    return {key: value / total for key, value in data.items()}


def compute_sdi(scores, weights=None):
    """
    SR-04 — SDI = Σ (Ki × Wi).

    `scores` — {komponent_kodi: 0..100}. Yo'q komponent 0 deb olinadi.
    """
    normalized = normalize_weights(weights)
    total = 0.0
    for component, weight in normalized.items():
        total += float(scores.get(component) or 0.0) * weight
    return round(total, 2)
