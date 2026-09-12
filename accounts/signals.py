"""Foydalanuvchi yaratilganda profil va sozlamalarni avtomatik hosil qilish."""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if not created:
        return
    from notifications.models import NotificationSetting

    from .models import Profile

    from core.enums import Role

    # Superuser (createsuperuser) — avtomatik ADMIN roli; qolganlar TEACHER.
    role = Role.ADMIN if instance.is_superuser else Role.TEACHER
    Profile.objects.get_or_create(user=instance, defaults={"role": role, "roles": role})
    NotificationSetting.objects.get_or_create(user=instance)
