"""Shablonlarda o'qilmagan bildirishnomalar sonini ko'rsatish uchun."""

from .models import Notification


def unread_notifications(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"unread_notifications": 0, "latest_notifications": []}
    queryset = Notification.objects.filter(user=user)
    return {
        "unread_notifications": queryset.filter(read_at__isnull=True).count(),
        "latest_notifications": list(queryset[:5]),
    }
