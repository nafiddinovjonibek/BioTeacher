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
}


@login_required
def module_list(request, module):
    """Modul bo'yicha topshiriqlar ro'yxati."""
    if module not in Module.values:
        raise PermissionDenied("Noma'lum modul.")

    assignments = list(Assignment.objects.filter(module=module, is_active=True))
    submissions = {
        s.assignment_id: s for s in Submission.objects.filter(student=request.user)
    }
    # Shablonda lug'atni kalit bo'yicha o'qib bo'lmaydi — obyektga biriktiramiz.
    for assignment in assignments:
        assignment.my_submission = submissions.get(assignment.id)

    return render(
        request,
        "assignments/module_list.html",
        {"module": module, "meta": MODULE_META[Module(module)], "assignments": assignments},
    )


@login_required
def assignment_detail(request, slug):
    """
    Topshiriqni bajarish sahifasi (FR-22..FR-24).

    `action=save` — qoralama, `action=submit` — yakuniy yuborish.
    """
    assignment = get_object_or_404(Assignment, slug=slug, is_active=True)
    submission, _ = Submission.objects.get_or_create(
        assignment=assignment, student=request.user
    )

    if request.method == "POST" and not submission.is_editable:
        messages.error(request, "Bu ish allaqachon yuborilgan. Tahrirlash uchun mentordan ruxsat so'rang.")
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
    """FR-36 — ijodiy galereya: faqat rozilik bergan ishlar, o'z guruhi ichida."""
    profile = request.user.profile
    queryset = Submission.objects.filter(
        is_public=True,
        status__in=[Submission.Status.SUBMITTED, Submission.Status.GRADED],
    ).select_related("assignment", "student")
    if profile.group_id:
        queryset = queryset.filter(student__profile__group_id=profile.group_id)
    else:
        queryset = queryset.filter(student=request.user)
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
    """FR-55 — mentor rubrika bo'yicha baholaydi."""
    submission = get_object_or_404(
        Submission.objects.select_related("assignment__rubric", "student"), pk=pk
    )
    profile = getattr(request.user, "profile", None)
    is_mentor = (
        request.user.is_superuser
        or (profile and profile.is_teacher
            and getattr(submission.student.profile, "group", None)
            and submission.student.profile.group.teacher_id == request.user.pk)
    )
    if not is_mentor:
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
        messages.success(request, "Baho qo'yildi va talabaga xabar yuborildi.")
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
    if not (request.user.is_superuser or (profile and profile.is_teacher)):
        raise PermissionDenied("Faqat mentorlar uchun.")

    queryset = Submission.objects.filter(status=Submission.Status.SUBMITTED)
    if not request.user.is_superuser:
        queryset = queryset.filter(student__profile__group__teacher=request.user)
    queryset = queryset.select_related("assignment", "student", "student__profile__group")
    return render(request, "assignments/queue.html", {"submissions": queryset.order_by("submitted_at")})


@login_required
def reopen(request, pk):
    """Mentor qayta yuborishga ruxsat beradi (TZ 6.3)."""
    submission = get_object_or_404(Submission, pk=pk)
    profile = getattr(request.user, "profile", None)
    if not (request.user.is_superuser or (profile and profile.is_teacher)):
        raise PermissionDenied("Faqat mentorlar uchun.")
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
