"""Yutuqlar sahifasi (FR-49..FR-52). Ochiq reyting YO'Q — SR-07."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from progress.models import Streak

from .services import badge_board


@login_required
def achievements(request):
    from progress.services import current_sdi
    from gamification.services import metric_sdi_growth

    return render(
        request,
        "gamification/achievements.html",
        {
            "rows": badge_board(request.user),
            "streak": Streak.objects.filter(user=request.user).first(),
            "sdi": current_sdi(request.user),
            "growth": round(metric_sdi_growth(request.user), 1),
        },
    )
