"""Umumiy abstrakt modellar (TZ 6.3 — ma'lumotlar butunligi qoidalari)."""

from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False)

    def delete(self):
        """Guruhli o'chirish ham soft bo'ladi — tadqiqot ma'lumoti yo'qolmaydi."""
        return super().update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Standart menejer o'chirilganlarni yashiradi."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("yaratilgan", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("yangilangan", auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(TimeStampedModel):
    """
    TZ 6.3: barcha o'chirishlar soft delete.

    `objects` — faqat tirik yozuvlar; `all_objects` — hammasi (audit uchun).
    """

    is_deleted = models.BooleanField("o'chirilgan", default=False, db_index=True)
    deleted_at = models.DateTimeField("o'chirilgan sana", null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager.from_queryset(SoftDeleteQuerySet)()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
