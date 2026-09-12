"""
assignments — topshiriqlar, rubrikalar, ishlar va baholash.

TZ: FR-22..FR-37, FR-54, FR-55. Bir tizim beshta modulga xizmat qiladi:
Laboratoriya, Men-o'qituvchi, Raqamli biologiya, Kreativ, BioBilim.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.enums import BloomLevel, Component, Module
from core.models import SoftDeleteModel, TimeStampedModel


class Rubric(SoftDeleteModel):
    """FR-31, FR-37 — mezonli baholash jadvali."""

    title = models.CharField("rubrika", max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "rubrika"
        verbose_name_plural = "rubrikalar"

    def __str__(self):
        return self.title

    @property
    def max_total(self):
        return sum(c.max_score * c.weight for c in self.criteria.all()) or 1


class Criterion(TimeStampedModel):
    """Rubrika mezoni. `level_descriptions` — har bir ball uchun izoh."""

    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE, related_name="criteria")
    name = models.CharField("mezon", max_length=200)
    hint = models.CharField("izoh", max_length=300, blank=True)
    weight = models.FloatField("vazn", default=1.0)
    max_score = models.PositiveSmallIntegerField("maksimal ball", default=4)
    level_descriptions = models.JSONField(
        "daraja izohlari", default=dict, blank=True,
        help_text='Masalan: {"0": "Bajarilmagan", "4": "Namunali"}',
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "mezon"
        verbose_name_plural = "mezonlar"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    def scale(self):
        return list(range(0, self.max_score + 1))


class Assignment(SoftDeleteModel):
    """FR-22, FR-27, FR-32, FR-35 — topshiriq."""

    class Kind(models.TextChoices):
        LAB4 = "LAB4", "Laboratoriya (4 bosqichli)"
        LESSON_PLAN = "LESSON_PLAN", "Dars loyihasi konstruktori"
        CASE = "CASE", "Pedagogik keys"
        DIGITAL = "DIGITAL", "Raqamli mahsulot"
        CREATIVE = "CREATIVE", "Ijodiy topshiriq"
        VISUAL = "VISUAL", "Muammoli vizual keys"

    module = models.CharField("modul", max_length=12, choices=Module.choices)
    kind = models.CharField("turi", max_length=12, choices=Kind.choices)
    title = models.CharField("sarlavha", max_length=250)
    slug = models.SlugField(max_length=140, unique=True)
    section = models.ForeignKey(
        "content.Section", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assignments", verbose_name="fan",
    )
    body = models.TextField("topshiriq matni")
    context_note = models.TextField("vaziyat / sharoit", blank=True)
    # Vizual keys tasviri: yuklangan rasm yoki platformaning tayyor tasviri (static yo'li).
    image = models.ImageField(
        "tasvir", upload_to="assignments/visuals/%Y/%m/", blank=True,
        help_text="JPG, PNG yoki WEBP. Vizual keysda tahlil shu tasvir asosida olib boriladi.",
    )
    visual = models.CharField("tayyor tasvir", max_length=200, blank=True, help_text="static/ ichidagi yo'l.")
    image_alt = models.CharField(
        "tasvir tavsifi", max_length=300, blank=True,
        help_text="Tasvirni ko'ra olmaydigan foydalanuvchi uchun qisqa tavsif.",
    )
    component = models.CharField("komponent", max_length=3, choices=Component.choices)
    bloom_level = models.PositiveSmallIntegerField(
        "Bloom darajasi", choices=BloomLevel.choices, default=BloomLevel.APPLY
    )
    rubric = models.ForeignKey(
        Rubric, on_delete=models.PROTECT, related_name="assignments", verbose_name="rubrika"
    )
    reference_solution = models.TextField(
        "etalon yechim", blank=True, help_text="FR-24 — faqat ish yuborilgandan keyin ochiladi.",
    )
    estimated_minutes = models.PositiveSmallIntegerField("taxminiy vaqt (daq.)", default=30)
    allow_files = models.BooleanField("fayl biriktirish", default=True)
    difficulty = models.PositiveSmallIntegerField("murakkablik (1-5)", default=3)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "topshiriq"
        verbose_name_plural = "topshiriqlar"
        ordering = ["module", "difficulty", "title"]

    def __str__(self):
        return self.title

    @property
    def picture_url(self):
        """Tasvir manzili: yuklangan rasm ustun, bo'lmasa tayyor tasvir; yo'q bo'lsa — ""."""
        if self.image:
            return self.image.url
        if self.visual:
            from django.templatetags.static import static

            return static(self.visual)
        return ""

    def steps(self):
        """FR-22 — laboratoriya topshirig'ining 4 bosqichi."""
        if self.kind == self.Kind.LAB4:
            return [
                ("hypothesis", "1. Taxmin", "Nima kuzatiladi deb o'ylaysiz? Nima uchun?"),
                ("plan", "2. Tajriba rejasi", "Buni qanday tekshirasiz? Bosqichlarni yozing."),
                ("prediction", "3. Natija bashorati", "Kutilayotgan natija va uni izohlash."),
                ("conclusion", "4. Xulosa", "Biologik qonuniyat va uni darsda qanday qo'llaysiz?"),
            ]
        if self.kind == self.Kind.LESSON_PLAN:
            return [
                ("goal", "Dars maqsadi", "Ta'limiy, tarbiyaviy va rivojlantiruvchi maqsad."),
                ("stages", "Dars bosqichlari va vaqt", "Har bir bosqich va unga ajratilgan vaqt."),
                ("methods", "Metod va texnologiyalar", "Qaysi metod, nima uchun aynan shu?"),
                ("assessment", "Baholash", "O'quvchi natijasini qanday o'lchaysiz?"),
                ("resources", "Resurslar", "Ko'rgazma, raqamli vosita, tarqatma material."),
            ]
        if self.kind == self.Kind.CASE:
            return [
                ("problem", "Muammoni aniqlash", "Vaziyatdagi asosiy pedagogik muammo nimada?"),
                ("method", "Metod tanlash", "Qaysi metodni tanlaysiz va nega?"),
                ("task", "Topshiriq yaratish", "O'quvchilarga beriladigan aniq topshiriq."),
                ("fragment", "Dars fragmenti", "10-15 daqiqalik fragment ssenariysi."),
            ]
        if self.kind == self.Kind.VISUAL:
            return [
                ("observe", "1. Kuzatish", "Tasvirda nimani ko'ryapsiz? Faqat faktlarni sanab chiqing — hali izohlamang."),
                ("problem", "2. Muammo", "Qaysi holat g'ayrioddiy yoki kutilmagan? Muammoni bitta savol shaklida yozing."),
                ("explain", "3. Tushuntirish", "Biologik qonuniyatga tayanib javob bering. Tasvirdagi qaysi dalil fikringizni tasdiqlaydi?"),
                ("teach", "4. Darsda qo'llash", "Bu keysni o'quvchilar bilan qanday tahlil qilasiz? 2-3 ta yo'naltiruvchi savol tuzing."),
            ]
        return [("answer", "Javob", "Yechimingizni batafsil yozing.")]


class AssignedTask(TimeStampedModel):
    """FR-57 — mentor topshiriqni talabalarga tayinlaydi."""

    assignment = models.OneToOneField(
        Assignment, on_delete=models.CASCADE, related_name="assigned_task"
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="assignments_made"
    )
    deadline = models.DateTimeField("muddat", null=True, blank=True)
    note = models.TextField("izoh", blank=True)

    class Meta:
        verbose_name = "tayinlangan topshiriq"
        verbose_name_plural = "tayinlangan topshiriqlar"

    def __str__(self):
        return str(self.assignment)


class Submission(SoftDeleteModel):
    """
    FR-22..FR-26 — talabaning ishi.

    `payload` — bosqich kalitlari bo'yicha javoblar: {"hypothesis": "...", ...}.
    TZ 6.3: bir marta yuboriladi; qayta yuborish faqat mentor ruxsati bilan.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Qoralama"
        SELF_ASSESSED = "SELF", "O'zini baholadi"
        SUBMITTED = "SUBMITTED", "Yuborilgan"
        GRADED = "GRADED", "Baholangan"
        RETURNED = "RETURNED", "Qayta ishlashga qaytarilgan"

    assignment = models.ForeignKey(
        Assignment, on_delete=models.PROTECT, related_name="submissions"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions"
    )
    payload = models.JSONField("javoblar", default=dict, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="graded_submissions",
    )
    self_percent = models.FloatField("o'z bahosi (%)", null=True, blank=True)
    mentor_percent = models.FloatField("mentor bahosi (%)", null=True, blank=True)
    mentor_feedback = models.TextField("mentor fikri", blank=True)
    is_public = models.BooleanField(
        "ijodiy galereyada ko'rsatish", default=False, help_text="FR-36 — talaba roziligi bilan."
    )
    reopen_allowed = models.BooleanField("qayta yuborishga ruxsat", default=False)

    class Meta:
        verbose_name = "ish"
        verbose_name_plural = "ishlar"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["student", "status"])]

    def __str__(self):
        return f"{self.student} — {self.assignment}"

    @property
    def is_editable(self):
        return self.status in {self.Status.DRAFT, self.Status.SELF_ASSESSED} or self.reopen_allowed

    @property
    def is_locked(self):
        return not self.is_editable

    @property
    def final_percent(self):
        """Yakuniy ball: mentor bahosi ustun, bo'lmasa o'z bahosi."""
        if self.mentor_percent is not None:
            return self.mentor_percent
        return self.self_percent

    @property
    def assessment_gap(self):
        """FR-25 — baholash adekvatligi: o'z bahosi va mentor bahosi farqi."""
        if self.self_percent is None or self.mentor_percent is None:
            return None
        return round(self.self_percent - self.mentor_percent, 1)

    def can_see_reference(self):
        """FR-24 — etalon yechim faqat yuborilgandan keyin."""
        return self.status in {self.Status.SUBMITTED, self.Status.GRADED, self.Status.RETURNED}

    def answer_rows(self):
        """Bosqich yorlig'i bilan birga javoblar — shablonlarda ishlatiladi."""
        payload = self.payload or {}
        return [
            {"key": key, "label": label, "hint": hint, "text": payload.get(key, "")}
            for key, label, hint in self.assignment.steps()
        ]

    def mark_submitted(self):
        self.status = self.Status.SUBMITTED
        self.submitted_at = timezone.now()
        self.reopen_allowed = False
        self.save(update_fields=["status", "submitted_at", "reopen_allowed", "updated_at"])


class SubmissionFile(TimeStampedModel):
    """FR-26, FR-33 — biriktirilgan fayl."""

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="submissions/%Y/%m/")
    original_name = models.CharField(max_length=250, blank=True)
    size = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "biriktirilgan fayl"
        verbose_name_plural = "biriktirilgan fayllar"

    def __str__(self):
        return self.original_name or self.file.name


class Score(TimeStampedModel):
    """FR-25, FR-55 — mezon bo'yicha ball (o'zi yoki mentor tomonidan)."""

    class Scorer(models.TextChoices):
        SELF = "SELF", "O'zini baholash"
        MENTOR = "MENTOR", "Mentor bahosi"

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="scores")
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE, related_name="scores")
    scorer = models.CharField(max_length=6, choices=Scorer.choices)
    value = models.FloatField("ball")
    comment = models.TextField("izoh", blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "baho"
        verbose_name_plural = "baholar"
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "criterion", "scorer"], name="uniq_score_per_scorer"
            )
        ]

    def __str__(self):
        return f"{self.submission_id} {self.criterion} {self.get_scorer_display()}={self.value}"


class CompetencyItem(SoftDeleteModel):
    """FR-34 — "Men buni bajara olaman" checklist bandi."""

    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    component = models.CharField(max_length=3, choices=Component.choices, default=Component.ACT)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "kompetensiya bandi"
        verbose_name_plural = "kompetensiya checklisti"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class CompetencyCheck(TimeStampedModel):
    """Talabaning checklist bo'yicha o'z bahosi."""

    class Level(models.IntegerChoices):
        NO = 0, "Hali yo'q"
        PARTIAL = 1, "Qisman"
        YES = 2, "Bajara olaman"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="competency_checks"
    )
    item = models.ForeignKey(CompetencyItem, on_delete=models.CASCADE, related_name="checks")
    level = models.PositiveSmallIntegerField(choices=Level.choices, default=Level.NO)
    evidence = models.TextField("dalil / havola", blank=True)

    class Meta:
        verbose_name = "kompetensiya belgisi"
        verbose_name_plural = "kompetensiya belgilari"
        constraints = [
            models.UniqueConstraint(fields=["user", "item"], name="uniq_user_competency")
        ]

    def __str__(self):
        return f"{self.user} — {self.item} ({self.get_level_display()})"
