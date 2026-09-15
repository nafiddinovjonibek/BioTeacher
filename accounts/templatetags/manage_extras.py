"""Boshqaruv paneli (CRUD) uchun shablon teglari."""

import datetime

from django import template
from django.db import models
from django.utils import timezone
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

register = template.Library()

MAX_TEXT = 90


def _resolve(obj, accessor):
    """`user.email`, `get_kind_display`, `__str__`, `questions.count` kabi accessor'lar."""
    value = obj
    for part in accessor.split("."):
        if value is None:
            return None
        if part == "__str__":
            value = str(value)
            continue
        attr = getattr(value, part, None)
        if isinstance(attr, models.Manager):
            value = attr  # menejer chaqirilmaydi — "questions.count" kabi zanjir ishlashi uchun
        else:
            value = attr() if callable(attr) else attr
    return value


@register.simple_tag
def cell(obj, accessor):
    """Ro'yxat jadvalidagi bitta katak — turga qarab chiroyli formatlaydi."""
    value = _resolve(obj, accessor)
    if value is None or value == "":
        return mark_safe('<span class="text-slateg-400">—</span>')
    if isinstance(value, bool):
        if value:
            return mark_safe('<span class="inline-block rounded-full bg-brand-50 text-brand-700 px-2 text-xs">✓</span>')
        return mark_safe('<span class="text-slateg-400">—</span>')
    if isinstance(value, datetime.datetime):
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return value.strftime("%d.%m.%Y %H:%M")
    if isinstance(value, datetime.date):
        return value.strftime("%d.%m.%Y")
    if isinstance(value, float):
        return f"{value:.1f}".rstrip("0").rstrip(".")
    if isinstance(value, models.Model):
        return str(value)
    if accessor.endswith("picture_url"):
        return format_html('<img src="{}" alt="" class="h-10 w-14 rounded-md border border-slateg-200 bg-white object-contain">', value)
    text = str(value)
    if len(text) > MAX_TEXT:
        return format_html('<span title="{}">{}…</span>', text, text[:MAX_TEXT])
    return escape(text)


@register.simple_tag(takes_context=True)
def qs_set(context, **kwargs):
    """Joriy GET parametrlariga qiymat qo'shib/almashtirib query string qaytaradi."""
    params = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            params.pop(key, None)
        else:
            params[key] = value
    encoded = params.urlencode()
    return "?" + encoded if encoded else ""


@register.simple_tag(takes_context=True)
def qs_without(context, *keys):
    params = context["request"].GET.copy()
    for key in keys:
        params.pop(key, None)
    encoded = params.urlencode()
    return "?" + encoded if encoded else ""
