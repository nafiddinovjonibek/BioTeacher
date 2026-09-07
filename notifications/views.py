"""Bildirishnomalar markazi va sozlamalari (FR-64..FR-66)."""

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Notification, NotificationSetting


class NotificationSettingForm(forms.ModelForm):
    class Meta:
        model = NotificationSetting
        fields = [
            "email_graded", "email_deadline", "email_new_assignment",
            "email_weekly", "email_badge",
        ]
        labels = {
            "email_graded": "Ishim baholanganda email yuborilsin",
            "email_deadline": "Muddat yaqinlashganda eslatma",
            "email_new_assignment": "Yangi topshiriq haqida xabar",
            "email_weekly": "Haftalik rivojlanish xulosasi",
            "email_badge": "Yangi nishon haqida xabar",
        }


@login_required
def inbox(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, "notifications/inbox.html", {"notifications": notifications[:100]})


@login_required
def open_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_read()
    return redirect(notification.url or "notifications:inbox")


@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, read_at__isnull=True).update(
        read_at=timezone.now()
    )
    messages.success(request, "Barcha bildirishnomalar o'qilgan deb belgilandi.")
    return redirect("notifications:inbox")


@login_required
def settings_view(request):
    setting, _ = NotificationSetting.objects.get_or_create(user=request.user)
    form = NotificationSettingForm(request.POST or None, instance=setting)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sozlamalar saqlandi.")
        return redirect("notifications:settings")
    return render(request, "notifications/settings.html", {"form": form})
