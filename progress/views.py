"""Monitoring — "Mening rivojlanishim" (FR-43..FR-48)."""

import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from accounts.permissions import require_student_access
from assignments.services import assessment_gap_stats
from core.enums import CUT_ORDER, Component, level_for

from .models import ActivityLog, ProgressSnapshot
from .services import current_scores, current_sdi, dynamics_summary


def _monitoring_context(user):
    from diagnostics.models import Measurement

    measurements = list(
        Measurement.objects.filter(user=user, is_void=False).order_by("created_at")
    )
    by_cut = {m.cut: m for m in measurements}

    # FR-43 — radar: kesimlar ustma-ust.
    radar = {
        "labels": [Component(c).label for c in Component.values],
        "datasets": [],
    }
    for cut in CUT_ORDER:
        measurement = by_cut.get(cut.value)
        if measurement:
            radar["datasets"].append(
                {
                    "label": cut.label,
                    "data": [round(measurement.as_dict()[c], 1) for c in Component.values],
                }
            )
    current = current_scores(user)
    radar["datasets"].append(
        {
            "label": "Joriy holat",
            "data": [round(current[c], 1) for c in Component.values],
            "current": True,
        }
    )

    # FR-44 — SDI dinamikasi.
    snapshots = list(ProgressSnapshot.objects.filter(user=user).order_by("date"))
    line = {
        "labels": [s.date.strftime("%d.%m") for s in snapshots],
        "data": [round(s.sdi, 1) for s in snapshots],
    }

    # FR-45 — komponent × kesim jadvali.
    table = []
    for component in Component.values:
        row = {"code": component, "label": Component(component).label, "cells": []}
        values = []
        for cut in CUT_ORDER:
            measurement = by_cut.get(cut.value)
            value = round(measurement.as_dict()[component], 1) if measurement else None
            row["cells"].append(value)
            if value is not None:
                values.append(value)
        row["current"] = round(current[component], 1)
        row["delta"] = round(values[-1] - values[0], 1) if len(values) >= 2 else None
        row["level"] = level_for(row["current"])
        table.append(row)

    sdi_row = {"label": "Umumiy SDI", "cells": [], "code": "SDI"}
    sdi_values = []
    for cut in CUT_ORDER:
        measurement = by_cut.get(cut.value)
        value = round(measurement.sdi, 1) if measurement else None
        sdi_row["cells"].append(value)
        if value is not None:
            sdi_values.append(value)
    sdi_row["current"] = current_sdi(user)
    sdi_row["delta"] = round(sdi_values[-1] - sdi_values[0], 1) if len(sdi_values) >= 2 else None

    # FR-46 — faollik.
    activity_counts = {
        choice.value: ActivityLog.objects.filter(user=user, action=choice.value).count()
        for choice in ActivityLog.Action
    }

    from .services import biggest_movers, dashboard_context, growth_series

    series = growth_series(user, max_points=24)
    return {
        "series": series,
        "series_json": json.dumps(series, ensure_ascii=False) if series else "null",
        "movers": biggest_movers(user),
        "student": user,
        "radar_json": json.dumps(radar, ensure_ascii=False),
        "line_json": json.dumps(line, ensure_ascii=False),
        "table": table,
        "sdi_row": sdi_row,
        "cuts": CUT_ORDER,
        "summary": dynamics_summary(user),
        "activity": activity_counts,
        "streak": dashboard_context(user)["streak"],
        "gap": assessment_gap_stats(user),
        "measurements": measurements,
        "sdi": current_sdi(user),
        "level": level_for(current_sdi(user) or 0),
    }


@login_required
def monitoring(request):
    return render(request, "progress/monitoring.html", _monitoring_context(request.user))


@login_required
def observation(request):
    """Kuzatuv varaqasi — MOT, ACT, REF, CRE kanallari va ularni ko'rsatgan dalillar."""
    from .services import observation_sheet

    return render(request, "progress/observation.html", {"channels": observation_sheet(request.user)})


@login_required
def student_monitoring(request, user_id):
    """Admin foydalanuvchi kartochkasini ko'radi (NFR-12 tekshiruvi bilan)."""
    from django.contrib.auth import get_user_model

    student = get_object_or_404(get_user_model(), pk=user_id)
    require_student_access(request.user, student)
    context = _monitoring_context(student)
    context["is_mentor_view"] = True
    return render(request, "progress/monitoring.html", context)


@login_required
def report_pdf(request):
    """FR-48 — shaxsiy hisobotni PDF sifatida yuklab olish."""
    context = _monitoring_context(request.user)
    context["request"] = request
    html = render_to_string("progress/pdf/report.html", context)
    try:
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse(html)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="bioteacher-hisobot.pdf"'
    pisa.CreatePDF(html.encode("utf-8"), dest=response, encoding="utf-8")
    return response


@login_required
def daily_done(request):
    """FR-52 — kunlik 15 daqiqalik topshiriqni bajarilgan deb belgilash."""
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.utils import timezone

    from .services import daily_task_for, log_activity

    task = daily_task_for(request.user)
    if request.method == "POST" and not task.done:
        task.done = True
        task.done_at = timezone.now()
        task.note = request.POST.get("note", "")[:2000]
        task.save(update_fields=["done", "done_at", "note", "updated_at"])
        log_activity(request.user, ActivityLog.Action.DAILY, object_ref=task.title)

        from gamification.services import evaluate_badges

        evaluate_badges(request.user)
        messages.success(request, "Bugungi 15 daqiqalik rivojlanish bajarildi. Zanjir uzilmadi!")
    return redirect("home:dashboard")
