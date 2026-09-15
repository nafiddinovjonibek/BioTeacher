"""«3D simulyatsiyalar» va «Maktab o'quv-tajriba uchastkasi resurslari» sahifalari."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import PlotResource, Simulation


def _is_admin(user):
    profile = getattr(user, "profile", None)
    return bool(profile and profile.is_admin)


@login_required
def simulations(request):
    items = list(Simulation.objects.filter(is_active=True).select_related("section"))
    sections = {s.section.slug: s.section for s in items if s.section}
    current = request.GET.get("fan", "")
    if current not in sections:
        current = ""
    shown = [s for s in items if not current or (s.section and s.section.slug == current)]
    return render(
        request,
        "development/simulations.html",
        {
            "items": shown,
            "total": len(items),
            "sections": sorted(sections.values(), key=lambda s: (s.order, s.title)),
            "current": current,
            "is_admin": _is_admin(request.user),
        },
    )


@login_required
def simulation_detail(request, slug):
    request.menu_page = "sim3d"
    sim = get_object_or_404(Simulation.objects.select_related("section"), slug=slug, is_active=True)
    others = Simulation.objects.filter(is_active=True).exclude(pk=sim.pk)[:3]
    return render(
        request,
        "development/simulation_detail.html",
        {"sim": sim, "others": others, "is_admin": _is_admin(request.user)},
    )


@login_required
def plot(request):
    queryset = PlotResource.objects.filter(is_active=True)
    kind = request.GET.get("tur", "")
    season = request.GET.get("mavsum", "")
    if kind not in PlotResource.Kind.values:
        kind = ""
    if season not in PlotResource.Season.values:
        season = ""
    total = queryset.count()
    if kind:
        queryset = queryset.filter(kind=kind)
    if season:
        # «Butun yil» materiali har qanday mavsumda kerak.
        queryset = queryset.filter(season__in=[season, PlotResource.Season.ALL])
    return render(
        request,
        "development/plot.html",
        {
            "items": list(queryset),
            "total": total,
            "kinds": [(k, label, PlotResource.KIND_ICONS[k]) for k, label in PlotResource.Kind.choices],
            "seasons": PlotResource.Season.choices,
            "kind": kind,
            "season": season,
            "is_admin": _is_admin(request.user),
        },
    )


@login_required
def plot_detail(request, slug):
    request.menu_page = "plot"
    resource = get_object_or_404(PlotResource, slug=slug, is_active=True)
    related = PlotResource.objects.filter(is_active=True, kind=resource.kind).exclude(pk=resource.pk)[:3]
    return render(
        request,
        "development/plot_detail.html",
        {"resource": resource, "related": related, "is_admin": _is_admin(request.user)},
    )
