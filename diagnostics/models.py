"""
diagnostics — anketa, bilim testi, urinishlar va MUZLATILGAN o'lchovlar.

TZ: FR-06..FR-12, SR-01..SR-06, 6.3 (Measurement immutable).
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.enums import (
    DEFAULT_WEIGHTS,
    BloomLevel,
    Component,
    Cut,
    compute_sdi,
    level_for,
    normalize_weights,
)
from core.models import SoftDeleteModel, TimeStampedModel


class ScoringWeights(TimeStampedModel):
    """
    SR-04 / SR-05 — admin sozlaydigan komponent vaznlari.

    Faol profil bitta bo'ladi; har bir `Measurement` o'zi ishlatgan vaznlarni
    nusxa qilib saqlaydi, shuning uchun vazn o'zgarishi eski natijalarni buzmaydi.
    """

    name = models.CharField("nomi", max_length=120, default="Standart")
    mot = models.FloatField("MOT vazni", default=DEFAULT_WEIGHTS["MOT"])
    cog = models.FloatField("COG vazni", default=DEFAULT_WEIGHTS["COG"])
    act = models.FloatField("ACT vazni", default=DEFAULT_WEIGHTS["ACT"])
    ref = models.FloatField("REF vazni", default=DEFAULT_WEIGHTS["REF"])
    cre = models.FloatField("CRE vazni", default=DEFAULT_WEIGHTS["CRE"])
    is_active = models.BooleanField("faol", default=True)

    class Meta:
        verbose_name = "vaznlar profili"
        verbose_name_plural = "vaznlar profillari"

    def __str__(self):
        return f"{self.name} ({'faol' if self.is_active else 'arxiv'})"

    def as_dict(self):
        return normalize_weights(
            {"MOT": self.mot, "COG": self.cog, "ACT": self.act, "REF": self.ref, "CRE": self.cre}
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            ScoringWeights.objects.exclude(pk=self.pk).update(is_active=False)

    @classmethod
    def active_weights(cls):
        profile = cls.objects.filter(is_active=True).first()
        return profile.as_dict() if profile else normalize_weights()


class Questionnaire(SoftDeleteModel):
    """FR-07 / FR-08 — anketa (Likert) yoki bilim testi."""

    class Kind(models.TextChoices):
        LIKERT = "LIKERT", "Likert anketa (o'z-o'zini baholash)"
        TEST = "TEST", "Bilim testi"

    title = models.CharField("nomi", max_length=200)
    slug = models.SlugField("slug", max_length=80, unique=True)
    kind = models.CharField("turi", max_length=10, choices=Kind.choices)
    cut = models.CharField("kesim", max_length=12, choices=Cut.choices, default=Cut.INITIAL)
    description = models.TextField("tavsif", blank=True)
    instruction = models.TextField("ko'rsatma", blank=True)
    question_count = models.PositiveSmallIntegerField(
        "tanlanadigan savollar soni", default=0,
        help_text="0 — barcha savollar. Testda tasodifiy tanlanma uchun ishlatiladi (FR-08).",
    )
    time_limit_minutes = models.PositiveSmallIntegerField("vaqt limiti (daq.)", default=0)
    shuffle_questions = models.BooleanField("savollarni aralashtirish", default=True)
    is_active = models.BooleanField("faol", default=True)

    class Meta:
        verbose_name = "so'rovnoma"
        verbose_name_plural = "so'rovnomalar"
        ordering = ["cut", "kind"]

    def __str__(self):
        return f"{self.title} — {self.get_cut_display()}"

    @property
    def is_likert(self):
        return self.kind == self.Kind.LIKERT


class Question(SoftDeleteModel):
    """
    Savol. Har bir savol MAJBURIY ravishda komponent va Bloom darajasiga ega (TZ 6.3).
    """

    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.CASCADE, related_name="questions"
    )
    text = models.TextField("savol matni")
    component = models.CharField("komponent", max_length=3, choices=Component.choices)
    bloom_level = models.PositiveSmallIntegerField(
        "Bloom darajasi", choices=BloomLevel.choices, default=BloomLevel.KNOW
    )
    reverse_scored = models.BooleanField(
        "teskari baholanadi", default=False,
        help_text="FR-09 — 'Men ... qilmayman' tipidagi savollar uchun.",
    )
    explanation = models.TextField("izoh / to'g'ri javob sharhi", blank=True)
    order = models.PositiveSmallIntegerField("tartib", default=0)
    is_active = models.BooleanField("faol", default=True)

    class Meta:
        verbose_name = "savol"
        verbose_name_plural = "savollar"
        ordering = ["questionnaire", "order", "id"]

    def __str__(self):
        return self.text[:70]

    def correct_choice(self):
        return self.choices.filter(is_correct=True).first()


class Choice(TimeStampedModel):
    """Test savoli uchun variant. Likert savollarida ishlatilmaydi."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField("variant", max_length=500)
    is_correct = models.BooleanField("to'g'ri", default=False)
    order = models.PositiveSmallIntegerField("tartib", default=0)

    class Meta:
        verbose_name = "variant"
        verbose_name_plural = "variantlar"
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:60]


class Attempt(TimeStampedModel):
    """FR-11 — tugallanmagan urinish saqlanadi va davom ettiriladi."""

    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "Jarayonda"
        FINISHED = "FINISHED", "Yakunlangan"
        EXPIRED = "EXPIRED", "Vaqti tugagan"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts"
    )
    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.PROTECT, related_name="attempts"
    )
    cut = models.CharField("kesim", max_length=12, choices=Cut.choices, default=Cut.INITIAL)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.IN_PROGRESS)
    question_order = models.JSONField("savollar tartibi", default=list, blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    scores = models.JSONField("komponent natijalari", default=dict, blank=True)

    class Meta:
        verbose_name = "urinish"
        verbose_name_plural = "urinishlar"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user} — {self.questionnaire} ({self.get_status_display()})"

    @property
    def is_finished(self):
        return self.status == self.Status.FINISHED

    @property
    def deadline(self):
        limit = self.questionnaire.time_limit_minutes
        if not limit:
            return None
        return self.started_at + timezone.timedelta(minutes=limit)

    @property
    def is_expired(self):
        deadline = self.deadline
        return bool(deadline and timezone.now() > deadline and not self.is_finished)

    def questions(self):
        """Urinish boshlanganda muzlatilgan tartibda savollarni qaytaradi."""
        ids = self.question_order or []
        if not ids:
            return Question.objects.filter(questionnaire=self.questionnaire, is_active=True)
        mapping = {q.pk: q for q in Question.objects.filter(pk__in=ids).prefetch_related("choices")}
        return [mapping[pk] for pk in ids if pk in mapping]

    def answered_count(self):
        return self.answers.count()

    def progress_percent(self):
        total = len(self.question_order or []) or 1
        return round(self.answered_count() / total * 100)


class Answer(TimeStampedModel):
    """Bitta savolga berilgan javob."""

    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="answers")
    choice = models.ForeignKey(
        Choice, on_delete=models.SET_NULL, null=True, blank=True, related_name="answers"
    )
    value = models.PositiveSmallIntegerField("Likert qiymati (1-5)", null=True, blank=True)
    text_answer = models.TextField("matnli javob", blank=True)

    class Meta:
        verbose_name = "javob"
        verbose_name_plural = "javoblar"
        constraints = [
            models.UniqueConstraint(fields=["attempt", "question"], name="uniq_attempt_question")
        ]

    def __str__(self):
        return f"{self.attempt_id} / {self.question_id}"

    def normalized_percent(self):
        """Javobni 0..100 shkalasiga keltiradi."""
        question = self.question
        if question.questionnaire.is_likert:
            if self.value is None:
                return None
            raw = 6 - self.value if question.reverse_scored else self.value  # FR-09
            return (raw - 1) / 4 * 100
        if self.choice is None:
            return None
        return 100.0 if self.choice.is_correct else 0.0


class Measurement(TimeStampedModel):
    """
    SR-06 — kesim bo'yicha MUZLATILGAN o'lchov.

    TZ 6.3: yaratilgandan keyin o'zgartirilmaydi. Xato bo'lsa — `void()` qilinadi
    va yangisi yaratiladi.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="measurements"
    )
    cut = models.CharField("kesim", max_length=12, choices=Cut.choices)
    mot = models.FloatField(default=0)
    cog = models.FloatField(default=0)
    act = models.FloatField(default=0)
    ref = models.FloatField(default=0)
    cre = models.FloatField(default=0)
    sdi = models.FloatField("SDI", default=0)
    weights_json = models.JSONField("ishlatilgan vaznlar", default=dict)
    source = models.CharField("manba", max_length=40, default="diagnostics")
    is_void = models.BooleanField("bekor qilingan", default=False)
    void_reason = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name = "o'lchov"
        verbose_name_plural = "o'lchovlar"
        ordering = ["user", "created_at"]
        indexes = [models.Index(fields=["user", "cut"])]

    def __str__(self):
        return f"{self.user} {self.get_cut_display()} SDI={self.sdi:.1f}"

    def save(self, *args, **kwargs):
        if self.pk:
            allowed = {"is_void", "void_reason", "updated_at"}
            update_fields = set(kwargs.get("update_fields") or [])
            if not update_fields or not update_fields.issubset(allowed):
                raise ValidationError(
                    "Measurement muzlatilgan (TZ 6.3): o'zgartirish mumkin emas. "
                    "Xato bo'lsa void() qiling va yangi o'lchov yarating."
                )
        else:
            weights = self.weights_json or ScoringWeights.active_weights()
            self.weights_json = normalize_weights(weights)
            self.sdi = compute_sdi(self.as_dict(), self.weights_json)
        return super().save(*args, **kwargs)

    def void(self, reason=""):
        self.is_void = True
        self.void_reason = reason[:250]
        super().save(update_fields=["is_void", "void_reason", "updated_at"])

    def as_dict(self):
        return {"MOT": self.mot, "COG": self.cog, "ACT": self.act, "REF": self.ref, "CRE": self.cre}

    @property
    def level(self):
        return level_for(self.sdi)


class Recommendation(TimeStampedModel):
    """FR-12 — diagnostika natijasidan kelib chiqqan individual tavsiya."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recommendations"
    )
    measurement = models.ForeignKey(
        Measurement, on_delete=models.CASCADE, related_name="recommendations", null=True, blank=True
    )
    component = models.CharField(max_length=3, choices=Component.choices)
    title = models.CharField(max_length=250)
    body = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "tavsiya"
        verbose_name_plural = "tavsiyalar"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
