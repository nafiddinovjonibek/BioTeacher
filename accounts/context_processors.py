"""
Shablonlarga profil va oʻlchov holatini uzatuvchi kontekst protsessori.

Oʻlchov relsi (`partials/rail.html`) har bir sahifada koʻrinadi, shuning uchun
komponent ballari ham shu yerdan beriladi.
"""

from core.enums import Component, level_for


# Bo'lim slugiga mos ikonka. Yangi bo'lim qo'shilsa shu yerga bitta qator.
SECTION_ICONS = {
    "hujayra-biologiyasi": "microscope",
    "genetika": "dna",
    "ekologiya": "globe",
    "metodika": "users",
    "zoologiya": "paw",
    "botanika": "leaf",
    "anatomiya": "user",
    "mikrobiologiya": "atom",
}


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

    # Yon paneldagi "Bo'limlar" ro'yxati.
    from content.models import Section

    sections = []
    for section in Section.objects.filter(is_active=True).order_by("order", "title"):
        section.icon_name = SECTION_ICONS.get(section.slug, "leaf")
        sections.append(section)
    data["rail_sections"] = sections

    # Rels faqat talabaga oʻlchov koʻrsatadi; mentor va tadqiqotchida oʻz bali yoʻq.
    if profile.is_student or user.is_superuser:
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
