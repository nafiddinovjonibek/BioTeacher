"""Diagnostika view'lari (FR-06..FR-12)."""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from accounts.services import log_action
from core.enums import CUT_ORDER, Cut, level_for

from .models import Attempt, Choice, Measurement, Question, Questionnaire
from .services import finish_attempt, get_or_start_attempt, result_context, save_answer

LIKERT_LABELS = [
    (1, "Hech qachon"),
    (2, "Kamdan-kam"),
    (3, "Ba'zan"),
    (4, "Ko'pincha"),
    (5, "Doimo"),
]


#: Kartadagi ikonka va qisqa sarlavha — so'rovnoma turiga qarab.
#: Modeldagi to'liq nom ("Boshlang'ich diagnostika: ...") kesim sarlavhasini
#: takrorlaydi, shuning uchun kartada qisqasi ko'rsatiladi.
KIND_ICONS = {
    Questionnaire.Kind.LIKERT: "pen",
    Questionnaire.Kind.TEST: "clipboard",
}
KIND_TITLES = {
    Questionnaire.Kind.LIKERT: "O'z-o'zini baholash anketasi",
    Questionnaire.Kind.TEST: "Kasbiy bilim testi",
}


def _attempt_state(attempt):
    """Kartadagi holat: nishon matni, uslub va tugma yozuvi."""
    if attempt is None:
        return {"label": "Boshlanmagan", "tone": "pill-mute", "cta": "Boshlash", "done": False}
    if attempt.is_finished:
        return {"label": "Yakunlangan", "tone": "pill-ok", "cta": "Natijani ko'rish", "done": True}
    if attempt.is_expired or attempt.status == Attempt.Status.EXPIRED:
        return {"label": "Vaqti tugagan", "tone": "pill-stop", "cta": "Qayta boshlash", "done": False}
    return {"label": "Jarayonda", "tone": "pill-go", "cta": "Davom ettirish", "done": False}


@login_required
def index(request):
    """Kesimlar bo'yicha diagnostika ro'yxati va foydalanuvchining joriy holati."""
    # Dars mustahkamlash testlari (QUIZ) bu yerda ko'rsatilmaydi — ular
    # BioBilim darsining ichida yechiladi (FR-20).
    questionnaires = Questionnaire.objects.filter(
        is_active=True, kind__in=Questionnaire.DIAGNOSTIC_KINDS
    ).order_by("cut", "kind")

    attempts = {
        a.questionnaire_id: a
        for a in Attempt.objects.filter(user=request.user)
        .select_related("questionnaire")
        .order_by("started_at")
    }
    measurements = list(
        Measurement.objects.filter(user=request.user, is_void=False).order_by("created_at")
    )
    by_cut = {m.cut: m for m in measurements}

    # Kesimlar CUT_ORDER bo'yicha guruhlanadi: boshlang'ich → chorak → yakuniy.
    blocks = []
    for cut in CUT_ORDER:
        rows = []
        for questionnaire in questionnaires:
            if questionnaire.cut != cut:
                continue
            attempt = attempts.get(questionnaire.pk)
            rows.append({
                "q": questionnaire,
                "attempt": attempt,
                "icon": KIND_ICONS.get(questionnaire.kind, "clipboard"),
                "title": KIND_TITLES.get(questionnaire.kind, questionnaire.title),
                "count": questionnaire.question_count or questionnaire.questions.count(),
                "state": _attempt_state(attempt),
            })
        if not rows:
            continue
        done = sum(1 for row in rows if row["state"]["done"])
        blocks.append({
            "cut": cut,
            "label": Cut(cut).label,
            "rows": rows,
            "done": done,
            "total": len(rows),
            "measurement": by_cut.get(cut),
        })

    # Joriy kesim — birinchi tugallanmagani; hammasi tugagan bo'lsa oxirgisi.
    current = next((b for b in blocks if b["done"] < b["total"]), blocks[-1] if blocks else None)
    if current:
        current["is_current"] = True
        started = any(row["attempt"] is not None for row in current["rows"])
        if current["done"] == current["total"]:
            current["cta"] = "Barcha kesimlar yakunlangan"
        else:
            current["cta"] = (
                f"{current['label']} kesimni davom ettirish" if started
                else f"{current['label']} kesimni boshlash"
            )
        # Tugma birinchi tugallanmagan so'rovnomaga olib boradi.
        current["next_slug"] = next(
            (row["q"].slug for row in current["rows"] if not row["state"]["done"]),
            current["rows"][0]["q"].slug,
        )

    latest = measurements[-1] if measurements else None
    return render(
        request,
        "diagnostics/index.html",
        {
            "blocks": blocks,
            "current": current,
            "measurements": measurements,
            "latest": latest,
            "level": level_for(latest.sdi) if latest else None,
            "components": result_context(latest)["rows"] if latest else None,
            "recommendations": (
                latest.recommendations.filter(is_active=True) if latest else None
            ),
            "ring_offset": round(264 * (1 - (latest.sdi / 100 if latest else 0)), 1),
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

    if not attempt.questionnaire.is_diagnostic:
        # Dars testining natijasi darsning o'zida ko'rsatiladi (FR-20).
        lesson = attempt.questionnaire.lessons.filter(is_active=True).first()
        if lesson:
            return redirect(
                "content:lesson",
                section_slug=lesson.topic.section.slug,
                topic_slug=lesson.topic.slug,
                lesson_slug=lesson.slug,
            )
        return redirect("content:index")

    # Faqat SHU urinishdan tug'ilgan o'lchov — boshqasiga tushib ketmasin.
    measurement = (
        Measurement.objects.filter(user=attempt.user, source=f"attempt:{attempt.pk}")
        .order_by("-created_at")
        .first()
    )
    if measurement is None:
        messages.warning(request, "Natija hali hisoblanmadi.")
        return redirect("diagnostics:index")

    context = result_context(measurement)
    context["attempt"] = attempt
    return render(request, "diagnostics/result.html", context)
