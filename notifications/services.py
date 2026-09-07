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


def notify_group(group, kind, title, body="", url="", exclude=None):
    """Guruhdagi barcha faol talabalarga xabar (FR-57)."""
    from accounts.models import Enrollment

    created = []
    enrollments = Enrollment.objects.filter(group=group, is_active=True).select_related("student")
    for enrollment in enrollments:
        if exclude and enrollment.student_id == exclude.pk:
            continue
        created.append(notify(enrollment.student, kind, title, body, url))
    return created


def unread_count(user):
    return Notification.objects.filter(user=user, read_at__isnull=True).count()
