"""
goals — "Mening maqsadim" moduli (FR-13..FR-17).

SMART shablon: Maqsad · Muddat · Vazifalar · Resurslar · Kutilayotgan natija.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.enums import Component
from core.models import SoftDeleteModel, TimeStampedModel


class Goal(SoftDeleteModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Faol"
        DONE = "DONE", "Yakunlangan"
        DROPPED = "DROPPED", "To'xtatilgan"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals"
    )
    title = models.CharField("maqsad", max_length=250)
    component = models.CharField(
        "yo'naltirilgan komponent", max_length=3, choices=Component.choices,
        default=Component.ACT,
    )
    why = models.TextField("nima uchun bu maqsad?", blank=True)
    resources = models.TextField("resurslar", blank=True)
    expected_result = models.TextField("kutilayotgan natija", blank=True)
    start_date = models.DateField("boshlanish", default=timezone.localdate)
    deadline = models.DateField("muddat")
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.ACTIVE)
    completed_at = models.DateTimeField(null=True, blank=True)

    # FR-17 — mentor izohi va tasdig'i.
    mentor_comment = models.TextField("mentor izohi", blank=True)
    mentor_approved = models.BooleanField("mentor tasdiqladi", default=False)
    mentor_approved_at = models.DateTimeField(null=True, blank=True)

    reminder_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = "maqsad"
        verbose_name_plural = "maqsadlar"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @property
    def days_left(self):
        return (self.deadline - timezone.localdate()).days

    @property
    def is_overdue(self):
        return self.is_active and self.days_left < 0

    def progress_percent(self):
        """FR-14 — vazifalar checklisti bo'yicha avtomatik foiz."""
        tasks = list(self.tasks.all())
        if not tasks:
            return 0
        return round(sum(1 for t in tasks if t.is_done) / len(tasks) * 100)

    def can_close(self):
        """FR-16 — yopishdan oldin yakuniy refleksiya majburiy."""
        return self.reflections.exists()


class GoalTask(TimeStampedModel):
    """FR-14 — maqsad ostidagi haftalik vazifa."""

    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField("vazifa", max_length=250)
    week = models.PositiveSmallIntegerField("hafta", default=1)
    is_done = models.BooleanField("bajarildi", default=False)
    done_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "maqsad vazifasi"
        verbose_name_plural = "maqsad vazifalari"
        ordering = ["week", "order", "id"]

    def __str__(self):
        return self.title

    def toggle(self):
        self.is_done = not self.is_done
        self.done_at = timezone.now() if self.is_done else None
        self.save(update_fields=["is_done", "done_at", "updated_at"])
        return self.is_done
