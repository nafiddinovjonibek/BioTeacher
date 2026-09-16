"""
Sayt bo'ylab qidiruv (yuqori paneldagi qidiruv maydoni).

Bitta so'rov platformaning barcha ochiq kontenti bo'yicha qidiriladi va natijalar
bo'limlarga ajratib beriladi. Har bir guruh — {"label", "icon", "url", "items", "total"}:
`items` — ko'rsatiladigan natijalar (ko'pi bilan `PER_GROUP` ta), `total` — topilganlar soni.
"""

import re

from django.db.models import Q
from django.urls import reverse

MIN_LENGTH = 2  # Bitta harf bo'yicha qidirilmaydi — natija ma'nosiz bo'ladi.
PER_GROUP = 6
SNIPPET = 160

# Tutuq belgisi matnlarda turlicha yozilgan («o'simlik», «o‘simlik», «oʻsimlik»).
# Foydalanuvchi qaysi variantni yozishidan qat'i nazar natija chiqishi kerak.
APOSTROPHES = "'‘’ʻʼ`"


def _snippet(text, query):
    """Matndan qidirilgan so'z atrofidagi qisqa parcha."""
    text = re.sub(r"\s+", " ", (text or "")).strip()
    if not text:
        return ""
    lowered = text.lower()
    hits = [pos for pos in (lowered.find(v.lower()) for v in variants(query)) if pos >= 0]
    found = min(hits) if hits else -1
    if found <= 0:
        return text[:SNIPPET] + ("…" if len(text) > SNIPPET else "")
    start = max(0, found - SNIPPET // 3)
    piece = text[start:start + SNIPPET]
    return ("…" if start else "") + piece + ("…" if start + SNIPPET < len(text) else "")


def variants(query):
    """So'rovning tutuq belgisi variantlari: «o'simlik» ham, «o‘simlik» ham topilsin."""
    if not any(ch in query for ch in APOSTROPHES):
        return [query]
    base = re.sub(f"[{re.escape(APOSTROPHES)}]", "\x00", query)
    return [base.replace("\x00", ch) for ch in APOSTROPHES]


def _q(query, *fields):
    condition = Q()
    for text in variants(query):
        for field in fields:
            condition |= Q(**{f"{field}__icontains": text})
    return condition


def _group(label, icon, url, rows, total):
    return {"label": label, "icon": icon, "url": url, "items": rows, "total": total}


def _rows(queryset, query, *, link, text_field, meta=None):
    """Natija qatorlari: sarlavha, havola, parcha va qo'shimcha izoh."""
    rows = []
    for obj in queryset[:PER_GROUP]:
        rows.append({
            "title": obj.title,
            "url": link(obj),
            "text": _snippet(getattr(obj, text_field, ""), query),
            "meta": meta(obj) if meta else "",
        })
    return rows


def search(query):
    """Barcha bo'limlar bo'yicha qidiruv natijalari (bo'sh guruhlar tashlab ketiladi)."""
    from assignments.models import Assignment
    from content.models import Lesson, Section, Topic
    from development.models import PlotResource, Simulation
    from diagnostics.models import Questionnaire

    query = (query or "").strip()
    if len(query) < MIN_LENGTH:
        return []

    groups = []

    sections = Section.objects.filter(is_active=True).filter(_q(query, "title", "description"))
    groups.append(_group(
        "Fanlar", "library", reverse("content:index"),
        _rows(sections, query, text_field="description",
              link=lambda s: reverse("content:section", args=[s.slug])),
        sections.count(),
    ))

    topics = (Topic.objects.filter(is_active=True, section__is_active=True)
              .select_related("section").filter(_q(query, "title", "summary")))
    groups.append(_group(
        "Mavzular", "book", reverse("content:index"),
        _rows(topics, query, text_field="summary",
              link=lambda t: reverse("content:topic", args=[t.section.slug, t.slug]),
              meta=lambda t: t.section.title),
        topics.count(),
    ))

    lessons = (Lesson.objects.filter(is_active=True, topic__is_active=True)
               .select_related("topic__section").filter(_q(query, "title", "body")))
    groups.append(_group(
        "Darslar", "book", reverse("content:index"),
        _rows(lessons, query, text_field="body",
              link=lambda le: reverse("content:lesson", args=[le.topic.section.slug, le.topic.slug, le.slug]),
              meta=lambda le: le.topic.title),
        lessons.count(),
    ))

    tasks = Assignment.objects.filter(is_active=True).filter(_q(query, "title", "body", "context_note"))
    groups.append(_group(
        "Topshiriqlar", "clipboard", reverse("assignments:cases"),
        _rows(tasks, query, text_field="body",
              link=lambda a: reverse("assignments:detail", args=[a.slug]),
              meta=lambda a: a.get_module_display()),
        tasks.count(),
    ))

    simulations = (Simulation.objects.filter(is_active=True).select_related("section")
                   .filter(_q(query, "title", "summary", "body", "parts", "task")))
    groups.append(_group(
        "3D simulyatsiyalar", "box", reverse("development:simulations"),
        _rows(simulations, query, text_field="summary",
              link=lambda s: reverse("development:simulation", args=[s.slug]),
              meta=lambda s: s.section.title if s.section else ""),
        simulations.count(),
    ))

    resources = PlotResource.objects.filter(is_active=True).filter(_q(query, "title", "summary", "body"))
    groups.append(_group(
        "Tajriba uchastkasi resurslari", "sprout", reverse("development:plot"),
        _rows(resources, query, text_field="summary",
              link=lambda r: reverse("development:plot_resource", args=[r.slug]),
              meta=lambda r: r.get_kind_display()),
        resources.count(),
    ))

    surveys = (Questionnaire.objects.filter(is_active=True, kind__in=Questionnaire.DIAGNOSTIC_KINDS)
               .filter(_q(query, "title", "description")))
    diagnostics_url = reverse("diagnostics:index")
    groups.append(_group(
        "Diagnostika", "clipboard", diagnostics_url,
        _rows(surveys, query, text_field="description",
              link=lambda s: diagnostics_url, meta=lambda s: s.get_cut_display()),
        surveys.count(),
    ))

    return [group for group in groups if group["items"]]
