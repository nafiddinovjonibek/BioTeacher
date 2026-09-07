"""
Tadqiqotchi paneli (FR-58..FR-63).

Bu bo'limda F.I.Sh. KO'RSATILMAYDI — faqat anonim `respondent_id` (NFR-17).
"""

from django import forms
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from accounts.forms import StyledFormMixin
from accounts.models import StudyGroup
from accounts.permissions import researcher_required
from accounts.services import log_action
from core.enums import CUT_ORDER, Cut, StudyArm

from .models import ExportJob
from .services import (
    comparison_table,
    describe,
    independent_t,
    measurement_rows,
    refresh_stat_summary,
    stats_table,
    to_csv,
    to_xlsx,
)


class ExportForm(StyledFormMixin, forms.Form):
    fmt = forms.ChoiceField(
        label="Format", choices=ExportJob.Format.choices, initial=ExportJob.Format.XLSX
    )
    cuts = forms.MultipleChoiceField(
        label="Kesimlar", choices=Cut.choices, required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Bo'sh qoldirilsa — barcha kesimlar.",
    )
    arms = forms.MultipleChoiceField(
        label="Guruhlar", choices=StudyArm.choices, required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Bo'sh qoldirilsa — barcha guruhlar.",
    )


class ArmForm(StyledFormMixin, forms.ModelForm):
    """FR-58 — guruhni tajriba yoki nazorat bo'linmasiga biriktirish."""

    class Meta:
        model = StudyGroup
        fields = ["study_arm"]
        labels = {"study_arm": "Tadqiqot guruhi"}


@researcher_required
def dashboard(request):
    """Tadqiqot paneli: guruhlar, o'lchovlar soni, qamrov."""
    from diagnostics.models import Measurement

    groups = StudyGroup.objects.select_related("teacher").order_by("study_arm", "name")
    rows = measurement_rows()
    coverage = []
    for cut in CUT_ORDER:
        cut_rows = [r for r in rows if r["cut"] == cut.value]
        coverage.append(
            {
                "cut": cut,
                "total": len(cut_rows),
                "experimental": sum(1 for r in cut_rows if r["group"] == StudyArm.EXPERIMENTAL),
                "control": sum(1 for r in cut_rows if r["group"] == StudyArm.CONTROL),
            }
        )
    consented = StudyGroup.objects.none()
    from accounts.models import Profile

    return render(
        request,
        "research/dashboard.html",
        {
            "groups": groups,
            "coverage": coverage,
            "total_measurements": Measurement.objects.filter(is_void=False).count(),
            "consented": Profile.objects.filter(research_consent=True).count(),
            "participants": Profile.objects.filter(group__isnull=False).count(),
        },
    )


@researcher_required
def set_arm(request, group_id):
    group = StudyGroup.objects.filter(pk=group_id).first()
    if group is None:
        messages.error(request, "Guruh topilmadi.")
        return redirect("research:dashboard")
    form = ArmForm(request.POST or None, instance=group)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "research.set_arm", group.name, arm=group.study_arm)
        messages.success(request, f"\"{group.name}\" guruhi yangilandi.")
        return redirect("research:dashboard")
    return render(request, "research/set_arm.html", {"form": form, "group": group})


@researcher_required
def export(request):
    """FR-59, FR-60 — anonim CSV/XLSX eksport."""
    form = ExportForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cuts = form.cleaned_data["cuts"] or None
        arms = form.cleaned_data["arms"] or None
        rows = measurement_rows(cuts=cuts, arms=arms)
        stamp = timezone.now().strftime("%Y%m%d-%H%M")

        if form.cleaned_data["fmt"] == ExportJob.Format.XLSX:
            payload = to_xlsx(rows)
            if payload is not None:
                filename = f"bioteacher-measurements-{stamp}.xlsx"
                response = HttpResponse(
                    payload,
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            else:
                messages.warning(request, "XLSX kutubxonasi topilmadi — CSV yuborildi.")
                payload, filename = to_csv(rows), f"bioteacher-measurements-{stamp}.csv"
                response = HttpResponse(payload, content_type="text/csv; charset=utf-8")
        else:
            filename = f"bioteacher-measurements-{stamp}.csv"
            response = HttpResponse(to_csv(rows), content_type="text/csv; charset=utf-8")

        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        ExportJob.objects.create(
            requested_by=request.user,
            fmt=form.cleaned_data["fmt"],
            cuts=cuts or [],
            arms=arms or [],
            row_count=len(rows),
            filename=filename,
        )
        log_action(request, "research.export", filename, rows=len(rows))
        return response

    return render(
        request,
        "research/export.html",
        {"form": form, "jobs": ExportJob.objects.all()[:20], "preview": measurement_rows()[:10]},
    )


@researcher_required
def statistics(request):
    """FR-61, FR-62 — tavsifiy statistika va guruhlararo taqqoslash."""
    rows = measurement_rows()
    table = stats_table(rows)
    comparison = comparison_table(rows)

    # SDI bo'yicha yakuniy kesimda E va C ni solishtirish (t-mezon kirish ma'lumoti).
    final_e = [r["SDI"] for r in rows if r["cut"] == Cut.FINAL and r["group"] == StudyArm.EXPERIMENTAL]
    final_c = [r["SDI"] for r in rows if r["cut"] == Cut.FINAL and r["group"] == StudyArm.CONTROL]
    t_test = independent_t(final_e, final_c)

    return render(
        request,
        "research/statistics.html",
        {
            "table": table,
            "comparison": comparison,
            "t_test": t_test,
            "final_e": describe(final_e),
            "final_c": describe(final_c),
        },
    )


@researcher_required
def refresh_stats(request):
    count = refresh_stat_summary()
    messages.success(request, f"Statistik kesh yangilandi: {count} qator.")
    return redirect("research:statistics")
