"""Landing va o'qituvchi dashboard'i (TZ 7.2)."""

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
    TZ 7.2 — o'qituvchining shaxsiy dashboard'i.

    Admin boshqaruv paneliga yo'naltiriladi.
    """
    profile = getattr(request.user, "profile", None)
    if profile is not None and profile.is_admin:
        return redirect("manage:students")

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


# Menyuda bor, lekin hali tayyorlanayotgan bo'limlar. Bo'lim tayyor bo'lganda
# `accounts.menu.PAGES` dagi URL'i almashtiriladi va shu yerdan o'chiriladi.
# related — (url nomi, argument, yorliq): hozir foydalanish mumkin bo'lgan yaqin bo'limlar.
UPCOMING = {
    "ai-sokratik": {
        "title": "AI-sokratik",
        "icon": "bot",
        "lead": "Sokratik suhbat usulidagi sun’iy intellekt yordamchisi. U tayyor javob bermaydi — "
                "yo‘naltiruvchi savollar orqali mavzuni o‘zingiz tahlil qilib, xulosaga kelishingizga yordam beradi.",
        "points": [
            "Mavzu yoki muammoni tanlaysiz — yordamchi savollar bilan fikringizni chuqurlashtiradi.",
            "Mulohazangizdagi bo‘shliqlarni ko‘rsatadi, yechimni esa sizga qoldiradi.",
            "Suhbat yakunidagi xulosani refleksiya kundaligiga saqlash mumkin bo‘ladi.",
        ],
        "related": [("content:index", None, "Mavzular"), ("reflection:journal", None, "Refleksiya kundaligi")],
    },
    "3d-simulyatsiyalar": {
        "title": "3D simulyatsiyalar",
        "icon": "box",
        "lead": "Hujayra, organlar tizimi va biologik jarayonlarning interaktiv 3D modellari: "
                "aylantirib, qismlarga ajratib, jarayonni bosqichma-bosqich kuzatib o‘rganasiz.",
        "points": [
            "Modelni istalgan tomondan ko‘rish va qismlarini alohida ajratish.",
            "Har bir simulyatsiyaga bog‘langan kuzatish topshirig‘i.",
        ],
        "related": [("content:index", None, "Mavzular"), ("assignments:module", "LAB", "Virtual laboratoriya")],
    },
    "tajriba-uchastkasi": {
        "title": "Maktab o‘quv-tajriba uchastkasi resurslari",
        "icon": "sprout",
        "lead": "Maktab o‘quv-tajriba uchastkasida amaliy mashg‘ulot o‘tkazish uchun metodik materiallar: "
                "tajriba rejalari, kuzatuv kundaliklari, fenologik taqvim va yo‘riqnomalar.",
        "points": [
            "Mavsum va sinf bo‘yicha saralangan tajriba rejalari.",
            "Yuklab olinadigan kuzatuv kundaligi va yo‘riqnoma shablonlari.",
        ],
        "related": [("assignments:module", "LAB", "Virtual laboratoriya"), ("content:index", None, "Mavzular")],
    },
}

# Tayyor bo'lgan bo'limlar: eski «tez orada» manzili yangi sahifaga olib boradi (saqlangan havolalar ishlasin).
READY = {
    "vizual-keyslar": "assignments:cases",
}


@login_required
def upcoming(request, slug):
    """Menyudagi hali tayyorlanayotgan bo'lim — nima bo'lishi va hozir qayerga borish mumkinligi."""
    from django.http import Http404
    from django.urls import reverse

    if slug in READY:
        return redirect(READY[slug])
    page = UPCOMING.get(slug)
    if page is None:
        raise Http404
    related = [
        {"href": reverse(name, args=[arg] if arg else None), "label": label}
        for name, arg, label in page["related"]
    ]
    return render(request, "home/upcoming.html", {"page": page, "related": related})


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
