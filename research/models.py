"""
research — tadqiqot moduli: eksport jurnali va statistik xulosalar (FR-58..FR-63).

Ma'lumot NFR-17 ga muvofiq anonimlashtiriladi: F.I.Sh. o'rniga `respondent_id`.
"""

from django.conf import settings
from django.db import models

from core.enums import Cut, StudyArm
from core.models import TimeStampedModel


class ExportJob(TimeStampedModel):
    """FR-59 — eksport jurnali (kim, qachon, qaysi kesimni yuklab oldi)."""

    class Format(models.TextChoices):
        CSV = "CSV", "CSV"
        XLSX = "XLSX", "XLSX"

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="exports"
    )
    fmt = models.CharField("format", max_length=5, choices=Format.choices, default=Format.CSV)
    cuts = models.JSONField("kesimlar", default=list, blank=True)
    arms = models.JSONField("guruhlar", default=list, blank=True)
    row_count = models.PositiveIntegerField("qatorlar soni", default=0)
    filename = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name = "eksport"
        verbose_name_plural = "eksportlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} — {self.fmt} ({self.row_count} qator)"


class StatSummary(TimeStampedModel):
    """
    FR-61 — kesim × guruh bo'yicha tavsifiy statistika keshi.

    Har safar qayta hisoblanishi mumkin; dissertatsiya jadvallarini tez chiqarish uchun.
    """

    cut = models.CharField(max_length=12, choices=Cut.choices)
    arm = models.CharField(max_length=1, choices=StudyArm.choices)
    component = models.CharField(max_length=5)  # komponent kodi yoki "SDI"
    n = models.PositiveIntegerField(default=0)
    mean = models.FloatField(default=0)
    sd = models.FloatField(default=0)
    minimum = models.FloatField(default=0)
    maximum = models.FloatField(default=0)

    class Meta:
        verbose_name = "statistik xulosa"
        verbose_name_plural = "statistik xulosalar"
        constraints = [
            models.UniqueConstraint(
                fields=["cut", "arm", "component"], name="uniq_stat_summary"
            )
        ]

    def __str__(self):
        return f"{self.cut}/{self.arm}/{self.component}: M={self.mean:.1f} SD={self.sd:.1f}"
