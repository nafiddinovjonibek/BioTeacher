"""Landing va talaba dashboard'i (TZ 7.2)."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.enums import COMPONENT_DESCRIPTIONS, Component


def landing(request):
    if request.user.is_authenticated:
        return redirect("home:dashboard")
    return render(
        request,
        "home/landing.html",
        {
            "components": [
                {
                    "code": component.value,
                    "label": component.label,
                    "description": COMPONENT_DESCRIPTIONS[component],
                }
                for component in Component
            ]
        },
    )


def about(request):
    return render(request, "home/about.html")


@login_required
def dashboard(request):
    """
    TZ 7.2 — talaba dashboard'i.

    Mentor/tadqiqotchi uchun o'z kabinetiga yo'naltiriladi.
    """
    profile = getattr(request.user, "profile", None)
    if profile is not None:
        if profile.is_teacher:
            return redirect("teacher:groups")
        if profile.is_researcher:
            return redirect("research:dashboard")

    import json

    from assignments.models import Submission
    from goals.models import Goal
    from progress.services import (
        biggest_movers, dashboard_context, growth_series, weakest_reading,
    )
    from reflection.models import ReflectionEntry

    context = dashboard_context(request.user)
    series = growth_series(request.user)
    context["series"] = series
    context["series_json"] = json.dumps(series) if series else "null"
    context["movers"] = biggest_movers(request.user)
    context["weakest"] = weakest_reading(request.user)
    # Progress halqasi: aylana uzunligi 2*pi*42 = 264.
    context["ring_offset"] = round(264 * (1 - (context.get("sdi") or 0) / 100), 1)

    from content.models import Lesson, LessonProgress
    from progress.models import ActivityLog

    passed = LessonProgress.objects.filter(
        user=request.user, status=LessonProgress.Status.PASSED
    ).count()
    context["lessons_passed"] = passed
    context["lessons_total"] = Lesson.objects.filter(is_active=True).count()
    context["recent_activity"] = (
        ActivityLog.objects.filter(user=request.user)
        .exclude(action=ActivityLog.Action.BADGE)[:4]
    )
    context.update(
        {
            "active_goal": Goal.objects.filter(
                user=request.user, status=Goal.Status.ACTIVE
            ).prefetch_related("tasks").first(),
            "last_reflection": ReflectionEntry.objects.filter(user=request.user).first(),
            "recent_badges": request.user.badges.select_related("badge")[:4],
            "pending_reflection": Submission.objects.filter(
                student=request.user,
                status__in=[Submission.Status.SUBMITTED, Submission.Status.GRADED],
                reflections__isnull=True,
            ).select_related("assignment")[:3],
            "recommendations": request.user.recommendations.filter(is_active=True),
        }
    )
    return render(request, "home/dashboard.html", context)


@login_required
def cabinet(request):
    """
    Shaxsiy kabinet — hisobga oid hamma narsa bir joyda.

    Bu sahifa oʻlchov koʻrsatmaydi: ular dashboard va rivojlanish tarixida.
    Bu yerda faqat foydalanuvchining OʻZIGA tegishli sozlamalar.
    """
    from notifications.models import NotificationSetting

    profile = getattr(request.user, "profile", None)
    setting, _ = NotificationSetting.objects.get_or_create(user=request.user)
    return render(
        request,
        "home/cabinet.html",
        {"profile": profile, "notification_setting": setting},
    )
