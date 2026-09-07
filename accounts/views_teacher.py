"""
O'qituvchi kabineti (TZ M12: FR-53..FR-57).

Mentor faqat O'Z guruhlaridagi talabalarni ko'radi (NFR-12).
"""

import statistics as stats_lib

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from core.enums import Component, level_for

from .forms import StudyGroupForm
from .models import Enrollment, StudyGroup
from .permissions import teacher_required
from .services import log_action

RISK_THRESHOLD = 50  # SDI shu qiymatdan past bo'lsa — xavf guruhi (FR-56)


def _mentor_groups(user):
    if user.is_superuser:
        return StudyGroup.objects.all()
    return StudyGroup.objects.filter(teacher=user)


def _student_rows(group):
    """Guruh talabalari: SDI, daraja, oxirgi faollik, tekshirilmagan ishlar."""
    from assignments.models import Submission
    from progress.models import ActivityLog
    from progress.services import current_sdi

    rows = []
    enrollments = (
        Enrollment.objects.filter(group=group, is_active=True)
        .select_related("student", "student__profile")
    )
    for enrollment in enrollments:
        student = enrollment.student
        sdi = current_sdi(student)
        last_activity = ActivityLog.objects.filter(user=student).order_by("-created_at").first()
        rows.append(
            {
                "student": student,
                "profile": getattr(student, "profile", None),
                "sdi": sdi,
                "level": level_for(sdi or 0),
                "last_activity": last_activity.created_at if last_activity else None,
                "pending": Submission.objects.filter(
                    student=student, status=Submission.Status.SUBMITTED
                ).count(),
                "at_risk": sdi is not None and sdi < RISK_THRESHOLD,
            }
        )
    return sorted(rows, key=lambda r: (r["sdi"] is None, r["sdi"] or 0))


@teacher_required
def groups(request):
    """FR-53 — guruhlar ro'yxati."""
    rows = []
    for group in _mentor_groups(request.user).order_by("name"):
        rows.append({"group": group, "count": group.student_count})
    return render(request, "teacher/groups.html", {"rows": rows})


@teacher_required
def group_create(request):
    form = StudyGroupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        group = form.save(commit=False)
        group.teacher = request.user
        group.save()
        log_action(request, "group.create", group.name)
        messages.success(
            request,
            f"Guruh yaratildi. Talabalarga kodni bering: {group.invite_code}",
        )
        return redirect("teacher:group_detail", pk=group.pk)
    return render(request, "teacher/group_form.html", {"form": form})


def _own_group(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)
    if not request.user.is_superuser and group.teacher_id != request.user.pk:
        raise PermissionDenied("Bu guruh sizga tegishli emas.")
    return group


@teacher_required
def group_detail(request, pk):
    """FR-53 — guruh va talabalar ro'yxati."""
    group = _own_group(request, pk)
    return render(
        request,
        "teacher/group_detail.html",
        {"group": group, "rows": _student_rows(group), "risk_threshold": RISK_THRESHOLD},
    )


@teacher_required
def analytics(request, pk):
    """FR-56 — guruh analitikasi: o'rtacha, mediana, eng zaif komponent, xavf guruhi."""
    group = _own_group(request, pk)
    rows = _student_rows(group)

    from progress.services import current_scores

    component_values = {c: [] for c in Component.values}
    sdis = []
    for row in rows:
        if row["sdi"] is None:
            continue
        sdis.append(row["sdi"])
        scores = current_scores(row["student"])
        for component in Component.values:
            component_values[component].append(scores[component])

    def summarize(values):
        if not values:
            return None
        return {
            "n": len(values),
            "mean": round(sum(values) / len(values), 1),
            "median": round(stats_lib.median(values), 1),
            "min": round(min(values), 1),
            "max": round(max(values), 1),
        }

    components = []
    for component in Component.values:
        summary = summarize(component_values[component])
        if summary:
            components.append({"code": component, "label": Component(component).label, **summary})

    weakest = min(components, key=lambda c: c["mean"]) if components else None
    at_risk = [row for row in rows if row["at_risk"]]

    return render(
        request,
        "teacher/analytics.html",
        {
            "group": group,
            "sdi": summarize(sdis),
            "components": components,
            "weakest": weakest,
            "at_risk": at_risk,
            "rows": rows,
            "risk_threshold": RISK_THRESHOLD,
        },
    )


@teacher_required
def student_card(request, pk, user_id):
    """FR-53 — talaba kartochkasi (monitoring sahifasiga yo'naltiradi)."""
    group = _own_group(request, pk)
    if not group.enrollments.filter(student_id=user_id, is_active=True).exists():
        raise PermissionDenied("Bu talaba sizning guruhingizda emas.")
    return redirect("progress:student", user_id=user_id)


@teacher_required
def announce(request, pk):
    """FR-57 — guruhga e'lon yoki topshiriq tayinlash."""
    from assignments.forms import AssignTaskForm
    from assignments.models import GroupAssignment
    from notifications.models import NotificationType
    from notifications.services import notify_group

    group = _own_group(request, pk)
    task_form = AssignTaskForm(request.POST or None)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "announce":
            title = request.POST.get("title", "").strip()
            body = request.POST.get("body", "").strip()
            if not title:
                messages.error(request, "E'lon sarlavhasini kiriting.")
            else:
                created = notify_group(
                    group, NotificationType.SYSTEM, title=title, body=body, exclude=request.user
                )
                log_action(request, "group.announce", group.name)
                messages.success(request, f"E'lon {len(created)} ta talabaga yuborildi.")
                return redirect("teacher:group_detail", pk=group.pk)
        elif action == "assign" and task_form.is_valid():
            assignment = task_form.cleaned_data["assignment"]
            GroupAssignment.objects.update_or_create(
                assignment=assignment,
                group=group,
                defaults={
                    "assigned_by": request.user,
                    "deadline": task_form.cleaned_data["deadline"],
                    "note": task_form.cleaned_data["note"],
                },
            )
            notify_group(
                group,
                NotificationType.NEW_ASSIGNMENT,
                title=f"Yangi topshiriq: {assignment.title}",
                body=task_form.cleaned_data["note"] or assignment.body[:300],
                url=f"/topshiriqlar/{assignment.slug}/",
                exclude=request.user,
            )
            log_action(request, "group.assign", assignment.slug)
            messages.success(request, "Topshiriq guruhga tayinlandi.")
            return redirect("teacher:group_detail", pk=group.pk)

    return render(request, "teacher/announce.html", {"group": group, "task_form": task_form})
