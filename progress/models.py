"""
progress — joriy komponent ballari, dinamika snapshotlari, faollik va streak.

TZ: FR-43..FR-48, FR-52, FR-67.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.enums import Component, level_for
from core.models import TimeStampedModel


class ComponentScore(TimeStampedModel):
    """
    Talabaning HOZIRGI komponent ko'rsatkichi (0..100).

    Bu qiymat o'zgaruvchan — u yangi topshiriq/refleksiyadan keyin qayta hisoblanadi.
    Muzlatilgan o'lchov uchun `diagnostics.Measurement` ishlatiladi (SR-06).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="component_scores"
    )
    component = models.CharField("komponent", max_length=3, choices=Component.choices)
    value = models.FloatField("ball (%)", default=0.0)
    diagnostic_part = models.FloatField("diagnostika ulushi", null=True, blank=True)
    practice_part = models.FloatField("amaliyot ulushi", null=True, blank=True)
    sample_size = models.PositiveIntegerField("hisobga olingan ish soni", default=0)
    computed_at = models.DateTimeField("hisoblangan", default=timezone.now)

    class Meta:
        verbose_name = "komponent bali"
        verbose_name_plural = "komponent ballari"
        constraints = [
            models.UniqueConstraint(fields=["user", "component"], name="uniq_user_component")
        ]

    def __str__(self):
        return f"{self.user} {self.component}={self.value:.1f}%"

    @property
    def level(self):
        return level_for(self.value)


class ProgressSnapshot(TimeStampedModel):
    """
    FR-44 — SDI dinamikasi uchun kunlik kesma.

    Har kuni ko'pi bilan bitta yozuv (o'sha kunning oxirgi holati).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progress_snapshots"
    )
    date = models.DateField("sana", default=timezone.localdate, db_index=True)
    mot = models.FloatField(default=0)
    cog = models.FloatField(default=0)
    act = models.FloatField(default=0)
    ref = models.FloatField(default=0)
    cre = models.FloatField(default=0)
    sdi = models.FloatField("SDI", default=0)

    class Meta:
        verbose_name = "rivojlanish kesmasi"
        verbose_name_plural = "rivojlanish kesmalari"
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(fields=["user", "date"], name="uniq_user_snapshot_date")
        ]

    def __str__(self):
        return f"{self.user} {self.date} SDI={self.sdi:.1f}"

    def as_dict(self):
        return {"MOT": self.mot, "COG": self.cog, "ACT": self.act, "REF": self.ref, "CRE": self.cre}


class ActivityLog(TimeStampedModel):
    """FR-46 — faollik jurnali (topshiriq, refleksiya, dars, diagnostika)."""

    class Action(models.TextChoices):
        DIAGNOSTIC_DONE = "DIAGNOSTIC", "Diagnostika yakunlandi"
        LESSON_DONE = "LESSON", "Dars o'zlashtirildi"
        SUBMISSION = "SUBMISSION", "Topshiriq yuborildi"
        REFLECTION = "REFLECTION", "Refleksiya yozildi"
        GOAL_CREATED = "GOAL", "Maqsad belgilandi"
        GOAL_TASK = "GOAL_TASK", "Maqsad vazifasi bajarildi"
        DAILY = "DAILY", "Kunlik 15 daqiqa bajarildi"
        BADGE = "BADGE", "Nishon olindi"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activities"
    )
    action = models.CharField(max_length=20, choices=Action.choices, db_index=True)
    object_ref = models.CharField("obyekt", max_length=200, blank=True)
    points = models.PositiveSmallIntegerField("faollik bali", default=1)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "faollik yozuvi"
        verbose_name_plural = "faollik jurnali"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} — {self.get_action_display()}"

    # Interfeys uchun: har bir harakat turiga ikonka va qisqa yorliq.
    ICONS = {
        "DIAGNOSTIC": "clipboard", "LESSON": "book", "SUBMISSION": "flask",
        "REFLECTION": "pen", "GOAL": "target", "GOAL_TASK": "check",
        "DAILY": "calendar", "BADGE": "trophy",
    }
    SHORT = {
        "DIAGNOSTIC": "Test", "LESSON": "Dars", "SUBMISSION": "Topshiriq",
        "REFLECTION": "Refleksiya", "GOAL": "Maqsad", "GOAL_TASK": "Vazifa",
        "DAILY": "Kunlik", "BADGE": "Nishon",
    }

    @property
    def icon(self):
        return self.ICONS.get(self.action, "spark")

    @property
    def short_label(self):
        return self.SHORT.get(self.action, self.get_action_display())


class Streak(TimeStampedModel):
    """FR-52 — muntazamlik (ketma-ket faol kunlar)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="streak"
    )
    current = models.PositiveIntegerField("joriy", default=0)
    longest = models.PositiveIntegerField("eng uzun", default=0)
    last_active_date = models.DateField("oxirgi faol kun", null=True, blank=True)
    total_active_days = models.PositiveIntegerField("jami faol kunlar", default=0)

    class Meta:
        verbose_name = "muntazamlik"
        verbose_name_plural = "muntazamlik"

    def __str__(self):
        return f"{self.user} — {self.current} kun"


class DailyTask(TimeStampedModel):
    """
    FR-52 — "Bugungi 15 daqiqalik rivojlanish".

    Har kuni talabaga bitta mikro-topshiriq tayinlanadi.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="daily_tasks"
    )
    date = models.DateField(default=timezone.localdate, db_index=True)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    component = models.CharField(max_length=3, choices=Component.choices)
    done = models.BooleanField("bajarildi", default=False)
    done_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField("qisqa izoh", blank=True)

    class Meta:
        verbose_name = "kunlik topshiriq"
        verbose_name_plural = "kunlik topshiriqlar"
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=["user", "date"], name="uniq_user_daily_task")
        ]

    def __str__(self):
        return f"{self.date} — {self.title}"
