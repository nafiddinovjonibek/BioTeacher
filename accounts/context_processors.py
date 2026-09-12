"""
Shablonlarga profil va oʻlchov holatini uzatuvchi kontekst protsessori.

Oʻlchov relsi (`partials/rail.html`) har bir sahifada koʻrinadi, shuning uchun
komponent ballari ham shu yerdan beriladi.
"""

from core.enums import Component, level_for


def current_profile(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"profile": None}

    profile = getattr(user, "profile", None)
    data = {"profile": profile, "current_sdi": None, "current_level": None, "rail_scores": []}
    if profile is None:
        return data

    from progress.services import current_scores, current_sdi

    sdi = current_sdi(user)
    data["current_sdi"] = sdi
    if sdi is not None:
        code, name, wash, step, hint = level_for(sdi)
        data["current_level"] = {
            "code": code, "name": name, "wash": wash, "step": step, "hint": hint,
        }

    # Tekshirish navbati belgisi — faqat admin rejimida hisoblanadi.
    if profile.is_admin:
        from assignments.models import Submission

        data["review_count"] = Submission.objects.filter(status=Submission.Status.SUBMITTED).count()

    from notifications.models import Notification

    from .menu import active_sections, rail_menu

    # Yon paneldagi "Fanlar" ichma-ich ro'yxati.
    sections = active_sections()
    data["rail_sections"] = sections
    badges = {
        "review_count": data.get("review_count", 0),
        "unread_notifications": Notification.objects.filter(user=user, read_at__isnull=True).count(),
    }
    data["rail_menu"] = rail_menu(badges, sections, request)

    # Yon panelda oʻz oʻlchovlari — adminning oʻz bali yoʻq.
    if not profile.is_admin:
        scores = current_scores(user)
        data["rail_scores"] = [
            {
                "code": component,
                "label": Component(component).label,
                "value": round(scores[component]),
                "step": level_for(scores[component])[3],
            }
            for component in Component.values
        ]
    return data
