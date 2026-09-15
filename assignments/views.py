"""
Topshiriq view'lari — beshta modulga xizmat qiladi (FR-22..FR-37).

Modul URL orqali ajratiladi: /laboratoriya/, /pedagog/, /raqamli/, /kreativ/.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from accounts.permissions import require_student_access
from accounts.services import log_action
from core.enums import Component, Module

from .forms import (
    GalleryConsentForm,
    MentorGradeForm,
    SelfAssessmentForm,
    StepAnswerForm,
    SubmissionFileForm,
)
from .models import Assignment, CompetencyCheck, CompetencyItem, Score, Submission
from .services import apply_scores, finalize_submission, notify_graded

MODULE_META = {
    Module.LAB: {
        "title": "Biologik laboratoriya",
        "lead": "Muammoli biologik vaziyatlar. Taxmin qiling, tajriba rejasini tuzing, "
                "natijani bashorat qiling va xulosangizni darsga bog'lang.",
    },
    Module.TEACHER: {
        "title": "Men — bo'lajak o'qituvchiman",
        "lead": "Haqiqiy pedagogik vaziyatlar va dars loyihasi konstruktori.",
    },
    Module.DIGITAL: {
        "title": "Raqamli biologiya",
        "lead": "Infografika, diagramma, interaktiv topshiriq va raqamli ta'lim resurslari.",
    },
    Module.CREATIVE: {
        "title": "Kreativ o'qituvchi",
        "lead": "Bir mavzuni noodatiy usulda tushuntirishning ijodiy yechimlari.",
    },
    Module.BIOKNOWLEDGE: {
        "title": "BioBilim topshiriqlari",
        "lead": "Kasbiy bilimni mustahkamlovchi amaliy topshiriqlar.",
    },
    Module.VISUAL: {
        "title": "Muammoli vizual keyslar",
        "lead": "Mikrofotosurat, grafik, sxema va o'quvchi ishlari asosidagi muammoli vaziyatlar. "
                "Tasvirni kuzating, muammoni aniqlang, tushuntiring va darsda qanday ishlatishingizni yozing.",
    },
}


#: Modul kartasining ikonkasi (partials/icon.html nomlari).
MODULE_ICONS = {
    Module.LAB: "microscope",
    Module.TEACHER: "users",
    Module.DIGITAL: "globe",
    Module.CREATIVE: "spark",
    Module.BIOKNOWLEDGE: "book",
    Module.VISUAL: "image",
}

#: Vizual keysni tahlil qilish bosqichlari — ro'yxat sahifasidagi qisqa yo'riqnoma.
VISUAL_STEPS = [
    ("Kuzating", "Tasvirdagi faktlarni izohsiz sanab chiqing."),
    ("Muammoni toping", "Nima g'ayrioddiy? Uni savolga aylantiring."),
    ("Tushuntiring", "Qonuniyatni tasvirdagi dalil bilan bog'lang."),
    ("Darsga ko'chiring", "O'quvchilar uchun yo'naltiruvchi savollar tuzing."),
]

#: «Virtual laboratoriya va amaliy topshiriqlar» menyu bandi ostidagi yorliqlar.
PRACTICE_TABS = [
    (Module.LAB, "Laboratoriya"),
    (Module.TEACHER, "Men — o‘qituvchi"),
    (Module.DIGITAL, "Raqamli biologiya"),
    (Module.CREATIVE, "Kreativ o‘qituvchi"),
]

#: Ish holati — kartadagi nishon uslubi va matni.
SUBMISSION_STATES = {
    Submission.Status.DRAFT: ("Qoralama", "pill-mute"),
    Submission.Status.SELF_ASSESSED: ("O'zini baholadi", "pill-info"),
    Submission.Status.SUBMITTED: ("Yuborilgan", "pill-go"),
    Submission.Status.GRADED: ("Baholangan", "pill-ok"),
    Submission.Status.RETURNED: ("Qayta ishlashga", "pill-stop"),
}


def _task_rows(user, assignments):
    """Topshiriq kartalari (ish holati bilan) va ixcham hisob: jami, boshlangan, baholangan."""
    submissions = {s.assignment_id: s for s in Submission.objects.filter(student=user)}
    rows = []
    for assignment in assignments:
        submission = submissions.get(assignment.id)
        label, tone = SUBMISSION_STATES.get(
            submission.status if submission else None, ("Boshlanmagan", "pill-mute")
        )
        rows.append({
            "a": assignment,
            "submission": submission,
            "label": label,
            "tone": tone,
            "done": bool(submission and submission.status == Submission.Status.GRADED),
        })

    done = sum(1 for row in rows if row["done"])
    started = sum(1 for row in rows if row["submission"])
    return rows, {
        "total": len(rows),
        "done": done,
        "started": started,
        "not_started": len(rows) - started,
        "percent": round(done / len(rows) * 100) if rows else 0,
    }


def _is_admin(user):
    profile = getattr(user, "profile", None)
    return bool(profile and profile.is_admin)


def _back_url(assignment):
    if assignment.module == Module.VISUAL:
        return reverse("assignments:cases")
    return reverse("assignments:module", args=[assignment.module])


@login_required
def module_list(request, module):
    """Modul bo'yicha topshiriqlar ro'yxati."""
    if module not in Module.values:
        raise PermissionDenied("Noma'lum modul.")
    if module == Module.VISUAL:
        return redirect("assignments:cases")

    rows, stats = _task_rows(
        request.user, Assignment.objects.filter(module=module, is_active=True).select_related("rubric")
    )
    return render(
        request,
        "assignments/module_list.html",
        {
            "module": module,
            "meta": MODULE_META[Module(module)],
            "icon": MODULE_ICONS.get(Module(module), "flask"),
            "tabs": [
                {"code": code.value, "label": label, "icon": MODULE_ICONS[code]} for code, label in PRACTICE_TABS
            ],
            "rows": rows,
            "is_admin": _is_admin(request.user),
            **stats,
        },
    )


@login_required
def cases(request):
    """«Muammoli vizual keyslar» — tasvir asosidagi muammoli vaziyatlarni mustaqil tahlil qilish."""
    assignments = list(
        Assignment.objects.filter(module=Module.VISUAL, is_active=True)
        .select_related("section").order_by("difficulty", "title")
    )
    sections = {a.section.slug: a.section for a in assignments if a.section}
    current = request.GET.get("fan", "")
    if current not in sections:
        current = ""
    rows, stats = _task_rows(request.user, assignments)
    if current:
        rows = [row for row in rows if row["a"].section and row["a"].section.slug == current]
    return render(
        request,
        "assignments/cases.html",
        {
            "meta": MODULE_META[Module.VISUAL],
            "rows": rows,
            "sections": sorted(sections.values(), key=lambda s: (s.order, s.title)),
            "current": current,
            "steps": VISUAL_STEPS,
            "is_admin": _is_admin(request.user),
            **stats,
        },
    )


def _mark_menu(request, assignment):
    """Vizual keys sahifalarida yon menyuda «Muammoli vizual keyslar» bandi faol ko'rinsin."""
    if assignment.module == Module.VISUAL:
        request.menu_page = "cases"


@login_required
def assignment_detail(request, slug):
    """
    Topshiriqni bajarish sahifasi (FR-22..FR-24).

    `action=save` — qoralama, `action=submit` — yakuniy yuborish.
    """
    assignment = get_object_or_404(Assignment.objects.select_related("section"), slug=slug, is_active=True)
    _mark_menu(request, assignment)
    submission, _ = Submission.objects.get_or_create(
        assignment=assignment, student=request.user
    )

    if request.method == "POST" and not submission.is_editable:
        messages.error(request, "Bu ish allaqachon yuborilgan. Tahrirlash uchun administratordan ruxsat so'rang.")
        return redirect("assignments:submission", pk=submission.pk)

    form = StepAnswerForm(
        request.POST or None,
        assignment=assignment,
        initial=submission.payload or None,
    )
    file_form = SubmissionFileForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "upload":
            if file_form.is_valid():
                uploaded = file_form.save(commit=False)
                uploaded.submission = submission
                uploaded.original_name = file_form.cleaned_data["file"].name[:250]
                uploaded.size = file_form.cleaned_data["file"].size
                uploaded.save()
                messages.success(request, "Fayl biriktirildi.")
                return redirect("assignments:detail", slug=slug)
        elif form.is_valid():
            submission.payload = {
                key: form.cleaned_data.get(key, "") for key, _, _ in assignment.steps()
            }
            submission.save(update_fields=["payload", "updated_at"])
            if action == "submit":
                # O'z bahosidan oldin yuborishga yo'l qo'yamiz, lekin eslatib qo'yamiz.
                return redirect("assignments:self_assess", pk=submission.pk)
            messages.success(request, "Qoralama saqlandi.")
            return redirect("assignments:detail", slug=slug)

    return render(
        request,
        "assignments/detail.html",
        {
            "assignment": assignment,
            "submission": submission,
            "form": form,
            "file_form": file_form,
            "steps": assignment.steps(),
            "meta": MODULE_META[Module(assignment.module)],
            "back_url": _back_url(assignment),
        },
    )


@login_required
def self_assess(request, pk):
    """FR-25 — avval o'zini baholaydi, keyin ish yuboriladi."""
    submission = get_object_or_404(
        Submission.objects.select_related("assignment__rubric"), pk=pk
    )
    if submission.student_id != request.user.pk:
        raise PermissionDenied("Bu ish sizga tegishli emas.")
    _mark_menu(request, submission.assignment)

    rubric = submission.assignment.rubric
    existing = {
        s.criterion_id: int(s.value)
        for s in submission.scores.filter(scorer=Score.Scorer.SELF)
    }
    form = SelfAssessmentForm(request.POST or None, rubric=rubric, initial_scores=existing)

    if request.method == "POST" and form.is_valid():
        apply_scores(submission, Score.Scorer.SELF, form.scores(), author=request.user)
        finalize_submission(submission)
        log_action(request, "submission.submit", submission.assignment.slug)
        messages.success(
            request,
            "Ishingiz yuborildi. Endi etalon yechim ochildi — o'z javobingiz bilan solishtiring.",
        )
        return redirect("assignments:reflect", pk=submission.pk)

    return render(
        request,
        "assignments/self_assess.html",
        {"submission": submission, "rubric": rubric, "form": form},
    )


@login_required
def reflect_redirect(request, pk):
    """FR-38 — ish yuborilgach majburiy refleksiyaga o'tkazadi."""
    submission = get_object_or_404(Submission, pk=pk, student=request.user)
    if submission.reflections.exists():
        return redirect("assignments:submission", pk=submission.pk)
    return redirect("reflection:create_for_submission", submission_id=submission.pk)


@login_required
def submission_detail(request, pk):
    """Yuborilgan ish: javoblar, etalon (FR-24), rubrika, mentor fikri."""
    submission = get_object_or_404(
        Submission.objects.select_related("assignment__rubric", "student"), pk=pk
    )
    require_student_access(request.user, submission.student)  # NFR-12
    _mark_menu(request, submission.assignment)

    consent_form = None
    if submission.student_id == request.user.pk:
        consent_form = GalleryConsentForm(request.POST or None, instance=submission)
        if request.method == "POST" and request.POST.get("action") == "gallery":
            if consent_form.is_valid():
                consent_form.save()
                messages.success(request, "Galereya sozlamasi yangilandi.")
                return redirect("assignments:submission", pk=pk)

    self_scores = {s.criterion_id: s for s in submission.scores.filter(scorer=Score.Scorer.SELF)}
    mentor_scores = {
        s.criterion_id: s for s in submission.scores.filter(scorer=Score.Scorer.MENTOR)
    }
    criteria = submission.assignment.rubric.criteria.all()
    rows = [
        {
            "criterion": criterion,
            "self": self_scores.get(criterion.id),
            "mentor": mentor_scores.get(criterion.id),
        }
        for criterion in criteria
    ]
    return render(
        request,
        "assignments/submission_detail.html",
        {
            "submission": submission,
            "rows": rows,
            "steps": submission.assignment.steps(),
            "consent_form": consent_form,
            "reflection": submission.reflections.first(),
        },
    )


@login_required
def submission_pdf(request, pk):
    """FR-30 — dars loyihasini PDF sifatida eksport qilish."""
    submission = get_object_or_404(Submission.objects.select_related("assignment"), pk=pk)
    require_student_access(request.user, submission.student)

    html = render_to_string(
        "assignments/pdf/submission.html",
        {"submission": submission, "steps": submission.assignment.steps(), "request": request},
    )
    try:
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse(html)  # PDF kutubxonasi yo'q — brauzerdan chop etish mumkin

    response = HttpResponse(content_type="application/pdf")
    filename = f"dars-loyihasi-{submission.pk}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    pisa.CreatePDF(html.encode("utf-8"), dest=response, encoding="utf-8")
    return response


@login_required
def gallery(request):
    """FR-36 — ijodiy galereya: faqat rozilik berilgan ishlar."""
    queryset = Submission.objects.filter(
        is_public=True,
        status__in=[Submission.Status.SUBMITTED, Submission.Status.GRADED],
    ).select_related("assignment", "student")
    return render(request, "assignments/gallery.html", {"submissions": queryset[:60]})


@login_required
def competency(request):
    """FR-34 — "Men buni bajara olaman" checklisti."""
    items = CompetencyItem.objects.filter(is_active=True)
    checks = {c.item_id: c for c in CompetencyCheck.objects.filter(user=request.user)}

    if request.method == "POST":
        for item in items:
            raw = request.POST.get(f"item{item.id}")
            if raw is None:
                continue
            CompetencyCheck.objects.update_or_create(
                user=request.user,
                item=item,
                defaults={
                    "level": int(raw),
                    "evidence": request.POST.get(f"evidence{item.id}", "")[:1000],
                },
            )
        messages.success(request, "Kompetensiya checklisti saqlandi.")
        return redirect("assignments:competency")

    total = items.count() * 2 or 1
    earned = sum(check.level for check in checks.values())
    return render(
        request,
        "assignments/competency.html",
        {
            "items": items,
            "checks": checks,
            "percent": round(earned / total * 100),
            "levels": CompetencyCheck.Level.choices,
        },
    )


# ------------------------------------------------------------- mentor tomoni

@login_required
def grade(request, pk):
    """FR-55 — admin rubrika bo'yicha baholaydi."""
    submission = get_object_or_404(
        Submission.objects.select_related("assignment__rubric", "student"), pk=pk
    )
    profile = getattr(request.user, "profile", None)
    if not bool(profile and profile.is_admin):
        raise PermissionDenied("Bu ishni baholash huquqingiz yo'q.")

    existing = {
        s.criterion_id: int(s.value)
        for s in submission.scores.filter(scorer=Score.Scorer.MENTOR)
    }
    form = MentorGradeForm(
        request.POST or None,
        rubric=submission.assignment.rubric,
        initial_scores=existing,
        initial={"feedback": submission.mentor_feedback},
    )
    if request.method == "POST" and form.is_valid():
        apply_scores(submission, Score.Scorer.MENTOR, form.scores(), author=request.user)
        submission.mentor_feedback = form.cleaned_data["feedback"]
        submission.save(update_fields=["mentor_feedback", "updated_at"])

        from progress.services import recompute

        recompute(submission.student)
        notify_graded(submission)
        log_action(request, "submission.grade", f"{submission.pk}")
        messages.success(request, "Baho qo'yildi va muallifga xabar yuborildi.")
        return redirect("assignments:queue")

    self_scores = {s.criterion_id: s for s in submission.scores.filter(scorer=Score.Scorer.SELF)}
    return render(
        request,
        "assignments/grade.html",
        {
            "submission": submission,
            "form": form,
            "steps": submission.assignment.steps(),
            "self_scores": self_scores,
        },
    )


@login_required
def queue(request):
    """FR-54 — tekshirish navbati."""
    profile = getattr(request.user, "profile", None)
    if not (profile and profile.is_admin):
        raise PermissionDenied("Faqat administrator uchun.")

    queryset = Submission.objects.filter(status=Submission.Status.SUBMITTED).select_related(
        "assignment", "student", "student__profile"
    )
    return render(request, "assignments/queue.html", {"submissions": queryset.order_by("submitted_at")})


@login_required
def reopen(request, pk):
    """Admin qayta yuborishga ruxsat beradi (TZ 6.3)."""
    submission = get_object_or_404(Submission, pk=pk)
    profile = getattr(request.user, "profile", None)
    if not (profile and profile.is_admin):
        raise PermissionDenied("Faqat administrator uchun.")
    submission.reopen_allowed = True
    submission.status = Submission.Status.RETURNED
    submission.save(update_fields=["reopen_allowed", "status", "updated_at"])

    from notifications.models import NotificationType
    from notifications.services import notify

    notify(
        submission.student,
        NotificationType.MENTOR_COMMENT,
        title=f"\"{submission.assignment.title}\" ishi qayta ishlashga qaytarildi",
        body=submission.mentor_feedback or "Mentor izohini ish sahifasida ko'ring.",
        url=f"/topshiriqlar/{submission.assignment.slug}/",
    )
    log_action(request, "submission.reopen", f"{submission.pk}")
    messages.success(request, "Ish qayta ishlashga qaytarildi.")
    return redirect("assignments:queue")
