"""Diagnostika view'lari (FR-06..FR-12)."""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from accounts.services import log_action

from .models import Attempt, Choice, Measurement, Question, Questionnaire
from .services import finish_attempt, get_or_start_attempt, result_context, save_answer

LIKERT_LABELS = [
    (1, "Hech qachon"),
    (2, "Kamdan-kam"),
    (3, "Ba'zan"),
    (4, "Ko'pincha"),
    (5, "Doimo"),
]


@login_required
def index(request):
    """Mavjud so'rovnomalar ro'yxati va foydalanuvchi holati."""
    questionnaires = Questionnaire.objects.filter(is_active=True).order_by("cut", "kind")
    attempts = {
        a.questionnaire_id: a
        for a in Attempt.objects.filter(user=request.user).order_by("started_at")
    }
    measurements = Measurement.objects.filter(user=request.user, is_void=False).order_by("created_at")
    return render(
        request,
        "diagnostics/index.html",
        {
            "questionnaires": questionnaires,
            "attempts": attempts,
            "measurements": measurements,
        },
    )


@login_required
def start(request, slug):
    questionnaire = get_object_or_404(Questionnaire, slug=slug, is_active=True)
    attempt, created = get_or_start_attempt(request.user, questionnaire)
    if created:
        log_action(request, "diagnostics.start", questionnaire.slug)
    return redirect("diagnostics:take", attempt_id=attempt.pk)


def _owned_attempt(request, attempt_id):
    attempt = get_object_or_404(
        Attempt.objects.select_related("questionnaire"), pk=attempt_id
    )
    if attempt.user_id != request.user.pk and not request.user.is_superuser:
        raise PermissionDenied("Bu urinish sizga tegishli emas.")  # NFR-12
    return attempt


@login_required
def take(request, attempt_id):
    """FR-11 — savollar sahifasi, javoblar avtomatik saqlanadi."""
    attempt = _owned_attempt(request, attempt_id)
    if attempt.is_finished:
        return redirect("diagnostics:result", attempt_id=attempt.pk)
    if attempt.is_expired:
        finish_attempt(attempt, expired=True)
        messages.warning(request, "Urinish vaqti tugadi.")
        return redirect("diagnostics:index")

    questions = attempt.questions()
    answered = {a.question_id: a for a in attempt.answers.all()}
    # Oldin berilgan javoblarni frontendda belgilash uchun (NFR-05 — avtosaqlash).
    answered_map = {
        str(question_id): (answer.value if answer.value is not None else answer.choice_id)
        for question_id, answer in answered.items()
    }
    return render(
        request,
        "diagnostics/take.html",
        {
            "attempt": attempt,
            "questions": questions,
            "answered": answered,
            "answered_map": json.dumps(answered_map),
            "likert_labels": LIKERT_LABELS,
            "total": len(questions),
        },
    )


@login_required
def answer(request, attempt_id):
    """HTMX orqali bitta javobni saqlaydi (FR-11 — avtosaqlash, NFR-05)."""
    if request.method != "POST":
        return HttpResponseBadRequest("POST kutilmoqda")
    attempt = _owned_attempt(request, attempt_id)
    if attempt.is_finished:
        return HttpResponseBadRequest("Urinish yakunlangan")

    question = get_object_or_404(Question, pk=request.POST.get("question_id"))
    if question.pk not in (attempt.question_order or []):
        raise PermissionDenied("Savol bu urinishga tegishli emas.")

    if attempt.questionnaire.is_likert:
        try:
            value = int(request.POST.get("value", ""))
        except ValueError:
            return HttpResponseBadRequest("Qiymat noto'g'ri")
        if not 1 <= value <= 5:
            return HttpResponseBadRequest("Qiymat 1..5 oralig'ida bo'lishi kerak")
        save_answer(attempt, question, value=value)
    else:
        choice = get_object_or_404(Choice, pk=request.POST.get("choice_id"), question=question)
        save_answer(attempt, question, choice=choice)

    return render(
        request,
        "diagnostics/_progress.html",
        {"attempt": attempt, "total": len(attempt.question_order or [])},
    )


@login_required
def finish(request, attempt_id):
    attempt = _owned_attempt(request, attempt_id)
    if attempt.is_finished:
        return redirect("diagnostics:result", attempt_id=attempt.pk)

    total = len(attempt.question_order or [])
    if attempt.answered_count() < total:
        messages.error(
            request,
            f"Barcha savollarga javob bering: {attempt.answered_count()}/{total} bajarildi.",
        )
        return redirect("diagnostics:take", attempt_id=attempt.pk)

    finish_attempt(attempt)
    log_action(request, "diagnostics.finish", attempt.questionnaire.slug)
    messages.success(request, "Diagnostika yakunlandi. Natijangiz tayyor.")
    return redirect("diagnostics:result", attempt_id=attempt.pk)


@login_required
def result(request, attempt_id):
    """FR-10 — natija: komponentlar, SDI, radar-diagramma, tavsiyalar."""
    attempt = _owned_attempt(request, attempt_id)
    if not attempt.is_finished:
        return redirect("diagnostics:take", attempt_id=attempt.pk)

    measurement = (
        Measurement.objects.filter(user=attempt.user, source=f"attempt:{attempt.pk}")
        .order_by("-created_at")
        .first()
    )
    if measurement is None:
        measurement = (
            Measurement.objects.filter(user=attempt.user, is_void=False)
            .order_by("-created_at")
            .first()
        )
    if measurement is None:
        messages.warning(request, "Natija hali hisoblanmadi.")
        return redirect("diagnostics:index")

    context = result_context(measurement)
    context["attempt"] = attempt
    return render(request, "diagnostics/result.html", context)
