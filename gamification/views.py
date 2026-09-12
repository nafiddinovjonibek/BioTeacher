"""Yutuqlar sahifasi (FR-49..FR-52). Ochiq reyting YO'Q — SR-07."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from progress.models import Streak

from .services import badge_board


@login_required
def achievements(request):
    from progress.services import current_sdi
    from gamification.services import metric_sdi_growth

    rows = badge_board(request.user)
    earned = [row for row in rows if row["earned"]]
    earned.sort(key=lambda row: row["earned"].created_at, reverse=True)
    # Olinmaganlari yaqinligi bo'yicha: eng ko'p bajarilgani birinchi.
    pending = sorted(
        (row for row in rows if not row["earned"]),
        key=lambda row: -(row["progress"] or 0),
    )

    total = len(rows)
    return render(
        request,
        "gamification/achievements.html",
        {
            "earned": earned,
            "pending": pending,
            "earned_count": len(earned),
            "total_count": total,
            "percent": round(len(earned) / total * 100) if total else 0,
            "streak": Streak.objects.filter(user=request.user).first(),
            "sdi": current_sdi(request.user),
            "growth": round(metric_sdi_growth(request.user), 1),
        },
    )
