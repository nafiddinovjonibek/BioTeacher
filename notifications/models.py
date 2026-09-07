"""notifications — ichki bildirishnomalar va email sozlamalari (FR-64..FR-66)."""

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import TimeStampedModel


class NotificationType(models.TextChoices):
    GRADED = "GRADED", "Ishingiz baholandi"
    DEADLINE = "DEADLINE", "Muddat yaqinlashmoqda"
    NEW_ASSIGNMENT = "NEW_ASSIGNMENT", "Yangi topshiriq"
    WEEKLY = "WEEKLY", "Haftalik xulosa"
    BADGE = "BADGE", "Yangi nishon"
    MENTOR_COMMENT = "MENTOR_COMMENT", "Mentor izohi"
    SYSTEM = "SYSTEM", "Tizim xabari"


class Notification(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    kind = models.CharField(max_length=20, choices=NotificationType.choices)
    title = models.CharField(max_length=250)
    body = models.TextField(blank=True)
    url = models.CharField(max_length=300, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "bildirishnoma"
        verbose_name_plural = "bildirishnomalar"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "read_at"])]

    def __str__(self):
        return self.title

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_read(self):
        if self.read_at is None:
            self.read_at = timezone.now()
            self.save(update_fields=["read_at", "updated_at"])


class NotificationSetting(TimeStampedModel):
    """FR-66 — foydalanuvchi bildirishnoma turlarini o'chira oladi."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_setting"
    )
    email_graded = models.BooleanField("baho qo'yilganda email", default=True)
    email_deadline = models.BooleanField("muddat eslatmasi", default=True)
    email_new_assignment = models.BooleanField("yangi topshiriq", default=True)
    email_weekly = models.BooleanField("haftalik xulosa", default=True)
    email_badge = models.BooleanField("nishon haqida", default=False)

    class Meta:
        verbose_name = "bildirishnoma sozlamasi"
        verbose_name_plural = "bildirishnoma sozlamalari"

    def __str__(self):
        return f"{self.user} sozlamalari"

    def allows_email(self, kind):
        mapping = {
            NotificationType.GRADED: self.email_graded,
            NotificationType.DEADLINE: self.email_deadline,
            NotificationType.NEW_ASSIGNMENT: self.email_new_assignment,
            NotificationType.WEEKLY: self.email_weekly,
            NotificationType.BADGE: self.email_badge,
        }
        return mapping.get(kind, True)
