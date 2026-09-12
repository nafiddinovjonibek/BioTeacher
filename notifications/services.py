"""Bildirishnoma yuborish (FR-64..FR-66)."""

from django.conf import settings
from django.core.mail import send_mail

from .models import Notification, NotificationSetting


def get_settings(user):
    setting, _ = NotificationSetting.objects.get_or_create(user=user)
    return setting


def notify(user, kind, title, body="", url="", send_email=True):
    """Ichki bildirishnoma yaratadi va sozlamaga qarab email yuboradi."""
    notification = Notification.objects.create(
        user=user, kind=kind, title=title, body=body, url=url
    )
    if send_email and user.email:
        setting = get_settings(user)
        if setting.allows_email(kind):
            send_mail(
                subject=f"{settings.SITE_NAME} — {title}",
                message=f"{body}\n\n{settings.SITE_URL}{url}" if url else body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
    return notification


def notify_students(kind, title, body="", url="", exclude=None):
    """Barcha faol o'qituvchilarga xabar (FR-57)."""
    from accounts.services import learner_queryset

    created = []
    for student in learner_queryset():
        if exclude and student.pk == exclude.pk:
            continue
        created.append(notify(student, kind, title, body, url))
    return created


def unread_count(user):
    return Notification.objects.filter(user=user, read_at__isnull=True).count()
