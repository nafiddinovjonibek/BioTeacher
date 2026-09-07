"""
reflection — refleksiya kundaligi (FR-38..FR-42).

4 majburiy savol har bir topshiriq yakunida; erkin yozuvlar esa istalgan vaqtda.
Refleksiya sifati rubrik bo'yicha baholanadi va REF komponentiga ta'sir qiladi (FR-41).
"""

from django.conf import settings
from django.db import models

from core.models import SoftDeleteModel, TimeStampedModel

MIN_ANSWER_LENGTH = 120  # FR-40


class ReflectionPrompt(TimeStampedModel):
    """
    FR-38 — 4 ta majburiy savol matni.

    Savollar rotatsiyasi (13-bo'lim, xatarlar) uchun bir nechta variant saqlanadi.
    """

    class Slot(models.IntegerChoices):
        LEARNED = 1, "Nimani o'rgandim?"
        DID_WELL = 2, "Nimani yaxshi bajardim?"
        TO_IMPROVE = 3, "Nimani rivojlantirishim kerak?"
        NEXT_TIME = 4, "Keyingi safar nimani boshqacha qilaman?"

    slot = models.PositiveSmallIntegerField("savol o'rni", choices=Slot.choices)
    text = models.CharField("savol matni", max_length=300)
    hint = models.CharField("yordamchi izoh", max_length=300, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "refleksiya savoli"
        verbose_name_plural = "refleksiya savollari"
        ordering = ["slot", "id"]

    def __str__(self):
        return f"{self.slot}. {self.text}"


class ReflectionEntry(SoftDeleteModel):
    """FR-38..FR-42 — kundalik yozuvi."""

    class Kind(models.TextChoices):
        TASK = "TASK", "Topshiriq refleksiyasi"
        FREE = "FREE", "Erkin yozuv"
        GOAL = "GOAL", "Maqsad yakuni"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reflections"
    )
    kind = models.CharField(max_length=6, choices=Kind.choices, default=Kind.TASK)
    submission = models.ForeignKey(
        "assignments.Submission", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reflections",
    )
    goal = models.ForeignKey(
        "goals.Goal", on_delete=models.SET_NULL, null=True, blank=True, related_name="reflections",
    )
    q1 = models.TextField("Nimani o'rgandim?", blank=True)
    q2 = models.TextField("Nimani yaxshi bajardim?", blank=True)
    q3 = models.TextField("Nimani rivojlantirishim kerak?", blank=True)
    q4 = models.TextField("Keyingi safar nimani boshqacha qilaman?", blank=True)
    free_text = models.TextField("erkin matn", blank=True)
    tags = models.CharField("teglar (vergul bilan)", max_length=250, blank=True)

    # FR-41 — sifat bahosi (avtomatik dastlabki + mentor tuzatishi mumkin).
    quality_score = models.FloatField("sifat bali (%)", null=True, blank=True)
    quality_detail = models.JSONField("sifat tafsiloti", default=dict, blank=True)
    mentor_comment = models.TextField("mentor izohi", blank=True)

    class Meta:
        verbose_name = "refleksiya"
        verbose_name_plural = "refleksiya kundaligi"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]

    def __str__(self):
        return f"{self.user} — {self.created_at:%d.%m.%Y}"

    @property
    def answers(self):
        return [self.q1, self.q2, self.q3, self.q4]

    @property
    def total_length(self):
        return sum(len(a.strip()) for a in self.answers) + len(self.free_text.strip())

    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    def preview(self, limit=160):
        text = self.q1 or self.free_text or self.q2 or ""
        return text[:limit] + ("…" if len(text) > limit else "")
