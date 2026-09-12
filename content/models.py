"""
content — "BioBilim" moduli: Fan → Mavzu → Dars → Material (FR-18..FR-21).
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.enums import Component
from core.models import SoftDeleteModel, TimeStampedModel


class Section(SoftDeleteModel):
    """FR-18 — eng yuqori daraja (masalan: "Hujayra biologiyasi")."""

    title = models.CharField("fan", max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField("tavsif", blank=True)
    icon = models.CharField("emoji", max_length=8, default="📚")
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "fan"
        verbose_name_plural = "fanlar"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title


class Topic(SoftDeleteModel):
    """FR-18 — fan ichidagi mavzu."""

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField("mavzu", max_length=200)
    slug = models.SlugField(max_length=120)
    summary = models.TextField("qisqacha", blank=True)
    component = models.CharField(
        "asosiy komponent", max_length=3, choices=Component.choices, default=Component.COG
    )
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "mavzu"
        verbose_name_plural = "mavzular"
        ordering = ["section", "order", "title"]
        constraints = [
            models.UniqueConstraint(fields=["section", "slug"], name="uniq_topic_slug_in_section")
        ]

    def __str__(self):
        return self.title


class Lesson(SoftDeleteModel):
    """FR-19, FR-20 — dars va uning mustahkamlash testi."""

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField("dars", max_length=250)
    slug = models.SlugField(max_length=140)
    body = models.TextField("dars matni", blank=True)
    video_url = models.URLField("video havola", blank=True)
    duration_minutes = models.PositiveSmallIntegerField("davomiyligi (daq.)", default=15)
    pass_threshold = models.PositiveSmallIntegerField(
        "o'zlashtirish chegarasi (%)", default=70, help_text="FR-20"
    )
    quiz = models.ForeignKey(
        "diagnostics.Questionnaire", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="lessons", verbose_name="mustahkamlash testi",
    )
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "dars"
        verbose_name_plural = "darslar"
        ordering = ["topic", "order", "title"]
        constraints = [
            models.UniqueConstraint(fields=["topic", "slug"], name="uniq_lesson_slug_in_topic")
        ]

    def __str__(self):
        return self.title


class Material(TimeStampedModel):
    """FR-19 — darsga biriktirilgan qo'shimcha material."""

    class Kind(models.TextChoices):
        TEXT = "TEXT", "Matn"
        IMAGE = "IMAGE", "Rasm"
        VIDEO = "VIDEO", "Video"
        PDF = "PDF", "PDF"
        LINK = "LINK", "Havola"

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="materials")
    kind = models.CharField(max_length=8, choices=Kind.choices, default=Kind.TEXT)
    title = models.CharField(max_length=250)
    body = models.TextField(blank=True)
    url = models.URLField(blank=True)
    file = models.FileField(upload_to="materials/%Y/%m/", blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "material"
        verbose_name_plural = "materiallar"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class LessonProgress(TimeStampedModel):
    """FR-20, FR-21 — talabaning dars bo'yicha holati."""

    class Status(models.TextChoices):
        STARTED = "STARTED", "Boshlangan"
        PASSED = "PASSED", "O'zlashtirildi"
        FAILED = "FAILED", "Qayta ko'rish kerak"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progress"
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.STARTED)
    score = models.FloatField("test natijasi (%)", null=True, blank=True)
    attempts = models.PositiveSmallIntegerField("urinishlar", default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "dars natijasi"
        verbose_name_plural = "dars natijalari"
        constraints = [
            models.UniqueConstraint(fields=["user", "lesson"], name="uniq_user_lesson")
        ]

    def __str__(self):
        return f"{self.user} — {self.lesson} ({self.get_status_display()})"

    def mark(self, score):
        """Test natijasiga qarab statusni belgilaydi (FR-20)."""
        self.score = score
        self.attempts += 1
        if score >= self.lesson.pass_threshold:
            self.status = self.Status.PASSED
            self.completed_at = timezone.now()
        else:
            self.status = self.Status.FAILED
        self.save()
        return self.status
