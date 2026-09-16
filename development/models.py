"""
development — «3-blok: O'z-o'zini rivojlantirish» resurslari.

• Simulation   — «3D simulyatsiyalar»: biologik obyektning 3D tasviri, qismlari va kuzatish topshirig'i.
• PlotResource — «Maktab o'quv-tajriba uchastkasi resurslari»: tajriba rejalari, kundaliklar, yo'riqnomalar.

Qolgan ikki band («Muammoli vizual keyslar», «Virtual laboratoriya») — `assignments.Assignment`.
Hammasini admin «Ma'lumotlar → 3-blok» bo'limida qo'shadi, tahrirlaydi va o'chiradi.
"""

import re

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from core.models import SoftDeleteModel

# «Nomi — izohi» qatori: tire, uzun tire yoki ikki nuqta bilan ajratiladi.
PART_SPLIT = re.compile(r"\s+[—–-]\s+|:\s+")


def _static_or_upload(image, visual):
    """Yuklangan fayl ustun, bo'lmasa platformaning tayyor tasviri (static yo'li); yo'q bo'lsa — ""."""
    if image:
        return image.url
    if visual:
        from django.templatetags.static import static

        return static(visual)
    return ""


def _lines(text):
    return [line.strip(" •-\t") for line in (text or "").splitlines() if line.strip(" •-\t")]


class Simulation(SoftDeleteModel):
    """3D simulyatsiya: interaktiv model o'rniga — 3D tasvir va unga bog'langan tahlil."""

    title = models.CharField(
        "nomi", max_length=200,
        help_text="Aniq, qisqa va o'quv dasturidagi mavzu nomiga mos. Masalan: «Yurakning 3D modeli».",
    )
    slug = models.SlugField(max_length=120, unique=True)
    section = models.ForeignKey(
        "content.Section", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="simulations", verbose_name="fan",
        help_text="Model qaysi fan (bo'lim) dasturiga tegishli — sahifada shu bo'yicha saralanadi.",
    )
    summary = models.CharField(
        "qisqa tavsif", max_length=300,
        help_text="Kartada ko'rinadigan 1-2 gap: model nimani va qanday ko'rinishda ko'rsatadi.",
    )
    image = models.ImageField(
        "3D tasvir", upload_to="simulations/%Y/%m/", blank=True,
        help_text="JPG, PNG, WEBP yoki GIF — modelning 3D ko'rinishi (render, skrinshot). "
                  "Real anatomik tuzilishni to'g'ri aks ettirishi shart.",
    )
    visual = models.CharField("tayyor tasvir", max_length=200, blank=True, help_text="static/ ichidagi yo'l.")
    image_alt = models.CharField(
        "tasvir tavsifi", max_length=300, blank=True,
        help_text="Rasm ostidagi qisqa tavsif: tasvirda nima va qaysi rakursda ko'rinadi. "
                  "Tasvirni ko'ra olmaydigan foydalanuvchi uchun ham shu matn o'qiladi.",
    )
    url = models.URLField(
        "havola", blank=True,
        help_text="Aylantirib ko'rish mumkin bo'lgan 3D model yoki video havolasi "
                  "(Sketchfab, BioDigital, YouTube va h.k.). Ixtiyoriy.",
    )
    body = models.TextField(
        "batafsil tavsif", blank=True,
        help_text="Mavzuning mohiyati: model nimani ko'rsatadi, tekis rasmdan farqi nimada. "
                  "Bo'sh qator — yangi xatboshi.",
    )
    parts = models.TextField(
        "asosiy qismlar", blank=True,
        help_text="Har qatorda bitta: «Nomi — vazifasi», qisqa va lo'nda. "
                  "Masalan: Yadro — irsiy axborotni saqlaydi",
    )
    task = models.TextField(
        "kuzatish topshirig'i", blank=True,
        help_text="Har qatorda bitta savol. Yodlashga emas — modelni aylantirib ko'rish, qismlarni "
                  "taqqoslash va sabab izlashga undasin.",
    )
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField("faol", default=True)

    class Meta:
        verbose_name = "3D simulyatsiya"
        verbose_name_plural = "3D simulyatsiyalar"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def clean(self):
        if not self.image and not self.visual:
            raise ValidationError({"image": "3D tasvirni yuklang."})

    @property
    def picture_url(self):
        return _static_or_upload(self.image, self.visual)

    def part_rows(self):
        """[(nomi, izohi), ...] — izoh bo'lmasa ikkinchisi ""."""
        rows = []
        for line in _lines(self.parts):
            name, *rest = PART_SPLIT.split(line, maxsplit=1)
            rows.append((name.strip(), rest[0].strip() if rest else ""))
        return rows

    def task_rows(self):
        return _lines(self.task)


class PlotResource(SoftDeleteModel):
    """Maktab o'quv-tajriba uchastkasida mashg'ulot o'tkazish uchun metodik material."""

    class Kind(models.TextChoices):
        PLAN = "PLAN", "Tajriba rejasi"
        DIARY = "DIARY", "Kuzatuv kundaligi"
        CALENDAR = "CALENDAR", "Fenologik taqvim"
        GUIDE = "GUIDE", "Yo'riqnoma"

    class Season(models.TextChoices):
        ALL = "ALL", "Butun yil"
        AUTUMN = "AUTUMN", "Kuz"
        WINTER = "WINTER", "Qish"
        SPRING = "SPRING", "Bahor"
        SUMMER = "SUMMER", "Yoz"

    KIND_ICONS = {Kind.PLAN: "flask", Kind.DIARY: "pen", Kind.CALENDAR: "calendar", Kind.GUIDE: "clipboard"}

    title = models.CharField("nomi", max_length=200)
    slug = models.SlugField(max_length=120, unique=True)
    kind = models.CharField("turi", max_length=10, choices=Kind.choices, default=Kind.PLAN)
    season = models.CharField("mavsum", max_length=10, choices=Season.choices, default=Season.ALL)
    grade = models.CharField("sinf", max_length=40, blank=True, help_text="Masalan: 6-sinf yoki 5–7-sinflar")
    duration = models.CharField("davomiyligi", max_length=60, blank=True, help_text="Masalan: 2 hafta, 1 dars")
    summary = models.CharField("qisqa tavsif", max_length=300, help_text="Kartada ko'rinadigan 1-2 gap.")
    body = models.TextField("mazmuni", help_text="Maqsad, jihozlar, bajarish tartibi va h.k. Bo'sh qator — yangi xatboshi.")
    image = models.ImageField("rasm", upload_to="plot/images/%Y/%m/", blank=True)
    file = models.FileField(
        "yuklab olinadigan fayl", upload_to="plot/files/%Y/%m/", blank=True,
        validators=[FileExtensionValidator(["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "odt", "jpg", "jpeg", "png", "zip"])],
        help_text="Shablon, jadval yoki yo'riqnoma: PDF, Word, Excel, PowerPoint, rasm yoki ZIP.",
    )
    url = models.URLField("tashqi havola", blank=True, help_text="Video yoki qo'shimcha manba (ixtiyoriy).")
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField("faol", default=True)

    class Meta:
        verbose_name = "tajriba uchastkasi resursi"
        verbose_name_plural = "tajriba uchastkasi resurslari"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    @property
    def icon(self):
        return self.KIND_ICONS.get(self.kind, "sprout")

    @property
    def file_name(self):
        return self.file.name.rsplit("/", 1)[-1] if self.file else ""

    def blocks(self):
        """
        Matn xatboshilari: [{"heading", "lines"}]. Xatboshining birinchi qatori butunlay
        katta harfda bo'lsa («JIHOZLAR») — u sarlavha sifatida ajratiladi.
        """
        out = []
        for chunk in re.split(r"\n\s*\n", (self.body or "").strip()):
            lines = [line.rstrip() for line in chunk.splitlines() if line.strip()]
            if not lines:
                continue
            first, heading = lines[0].strip(), ""
            if len(lines) > 1 and len(first) <= 60 and first == first.upper() and any(c.isalpha() for c in first):
                heading, lines = first.capitalize(), lines[1:]
            out.append({"heading": heading, "lines": lines})
        return out
