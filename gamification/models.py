"""
gamification — nishonlar va ularni berish qoidalari (FR-49..FR-52).

MUHIM (SR-07, FR-51): ochiq reyting jadvali YO'Q. Taqqoslash faqat
talabaning o'z oldingi natijasi bilan amalga oshiriladi.
"""

from django.conf import settings
from django.db import models

from core.models import SoftDeleteModel, TimeStampedModel


class Badge(SoftDeleteModel):
    """FR-49 — nishon."""

    code = models.SlugField("kod", max_length=60, unique=True)
    title = models.CharField("nomi", max_length=120)
    emoji = models.CharField("emoji", max_length=8, default="🏅")
    description = models.TextField("tavsif", blank=True)
    how_to_earn = models.CharField("qanday olinadi", max_length=250, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "nishon"
        verbose_name_plural = "nishonlar"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.emoji} {self.title}"


class BadgeRule(TimeStampedModel):
    """
    FR-50 — nishon berish sharti: metrika + chegara.

    Metrikalar `gamification.services.METRICS` da hisoblanadi.
    """

    class Metric(models.TextChoices):
        SUBMISSIONS_GRADED = "submissions_graded", "Baholangan ishlar soni"
        LAB_SUBMISSIONS = "lab_submissions", "Laboratoriya ishlari soni"
        LESSON_PLANS = "lesson_plans", "Yaratilgan dars loyihalari"
        CREATIVE_WORKS = "creative_works", "Ijodiy ishlar soni"
        DIGITAL_WORKS = "digital_works", "Raqamli mahsulotlar soni"
        REFLECTIONS = "reflections", "Refleksiya yozuvlari soni"
        LESSONS_PASSED = "lessons_passed", "O'zlashtirilgan darslar"
        STREAK = "streak", "Ketma-ket faol kunlar"
        GOALS_DONE = "goals_done", "Yakunlangan maqsadlar"
        SDI = "sdi", "Joriy SDI (%)"
        SDI_GROWTH = "sdi_growth", "SDI o'sishi (foiz punkti)"

    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="rules")
    metric = models.CharField("metrika", max_length=30, choices=Metric.choices)
    threshold = models.FloatField("chegara", default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "nishon qoidasi"
        verbose_name_plural = "nishon qoidalari"

    def __str__(self):
        return f"{self.badge} — {self.get_metric_display()} ≥ {self.threshold:g}"


class UserBadge(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges"
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="awards")
    reason = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name = "olingan nishon"
        verbose_name_plural = "olingan nishonlar"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "badge"], name="uniq_user_badge")
        ]

    def __str__(self):
        return f"{self.user} — {self.badge}"
