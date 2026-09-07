"""
Diagnostika servislari: urinishni boshlash, javob saqlash, natijani hisoblash.

TZ: FR-08 (tasodifiy tanlanma), FR-09 (aralashtirish, teskari savollar),
FR-10 (natija), FR-11 (davom ettirish), FR-12 (individual tavsiya).
"""

import random

from django.db import transaction
from django.utils import timezone

from core.enums import Component, COMPONENT_DESCRIPTIONS, level_for

from .models import Answer, Attempt, Measurement, Question, Recommendation, ScoringWeights


def build_question_order(questionnaire):
    """FR-08/FR-09 — tasodifiy tanlanma va aralashtirish, komponentlar muvozanati bilan."""
    questions = list(questionnaire.questions.filter(is_active=True))
    if not questions:
        return []

    limit = questionnaire.question_count or 0
    if limit and limit < len(questions):
        # Har bir komponentdan proporsional tanlaymiz — profil bir tomonlama chiqmasin.
        by_component = {}
        for question in questions:
            by_component.setdefault(question.component, []).append(question)
        per_component = max(1, limit // max(1, len(by_component)))
        selected = []
        for bucket in by_component.values():
            random.shuffle(bucket)
            selected.extend(bucket[:per_component])
        remaining = [q for q in questions if q not in selected]
        random.shuffle(remaining)
        selected.extend(remaining[: max(0, limit - len(selected))])
        questions = selected[:limit]

    if questionnaire.shuffle_questions:
        random.shuffle(questions)
    else:
        questions.sort(key=lambda q: (q.order, q.pk))
    return [q.pk for q in questions]


def get_or_start_attempt(user, questionnaire):
    """FR-11 — tugallanmagan urinish bo'lsa uni davom ettiradi."""
    attempt = Attempt.objects.filter(
        user=user, questionnaire=questionnaire, status=Attempt.Status.IN_PROGRESS
    ).first()
    if attempt:
        if attempt.is_expired:
            finish_attempt(attempt, expired=True)
        else:
            return attempt, False
    attempt = Attempt.objects.create(
        user=user,
        questionnaire=questionnaire,
        cut=questionnaire.cut,
        question_order=build_question_order(questionnaire),
    )
    return attempt, True


def save_answer(attempt, question, *, choice=None, value=None, text=""):
    """Bitta javobni saqlaydi (qayta javob berish urinishni yangilaydi)."""
    answer, _ = Answer.objects.update_or_create(
        attempt=attempt,
        question=question,
        defaults={"choice": choice, "value": value, "text_answer": text},
    )
    return answer


def compute_attempt_scores(attempt):
    """Urinish javoblarini komponentlar kesimida 0..100 ga aylantiradi."""
    buckets = {}
    for answer in attempt.answers.select_related("question", "choice"):
        percent = answer.normalized_percent()
        if percent is None:
            continue
        buckets.setdefault(answer.question.component, []).append(percent)
    return {
        component: round(sum(values) / len(values), 2)
        for component, values in buckets.items()
        if values
    }


@transaction.atomic
def finish_attempt(attempt, expired=False):
    """
    Urinishni yakunlaydi, ballarni hisoblaydi, kesim o'lchovini muzlatadi (SR-06)
    va individual tavsiyalarni yaratadi (FR-12).
    """
    attempt.scores = compute_attempt_scores(attempt)
    attempt.status = Attempt.Status.EXPIRED if expired else Attempt.Status.FINISHED
    attempt.finished_at = timezone.now()
    attempt.save(update_fields=["scores", "status", "finished_at", "updated_at"])

    if expired:
        return attempt, None

    from progress.services import log_activity, recompute
    from progress.models import ActivityLog

    recompute(attempt.user)
    measurement = create_measurement(attempt.user, attempt.cut, source=f"attempt:{attempt.pk}")
    build_recommendations(attempt.user, measurement)
    log_activity(
        attempt.user,
        ActivityLog.Action.DIAGNOSTIC_DONE,
        object_ref=attempt.questionnaire.title,
        points=3,
    )

    profile = getattr(attempt.user, "profile", None)
    if profile and not profile.onboarding_done:
        profile.onboarding_done = True
        profile.save(update_fields=["onboarding_done", "updated_at"])

    from gamification.services import evaluate_badges

    evaluate_badges(attempt.user)
    return attempt, measurement


def create_measurement(user, cut, source="diagnostics"):
    """
    SR-06 — kesim o'lchovini muzlatadi.

    Shu kesimning oldingi (bekor qilinmagan) o'lchovi bo'lsa, u void qilinadi:
    tarix saqlanadi, lekin faol o'lchov bitta bo'ladi.
    """
    from progress.services import current_scores

    scores = current_scores(user)
    Measurement.objects.filter(user=user, cut=cut, is_void=False).update(
        is_void=True, void_reason="Yangi o'lchov bilan almashtirildi"
    )
    return Measurement.objects.create(
        user=user,
        cut=cut,
        mot=scores[Component.MOT.value],
        cog=scores[Component.COG.value],
        act=scores[Component.ACT.value],
        ref=scores[Component.REF.value],
        cre=scores[Component.CRE.value],
        weights_json=ScoringWeights.active_weights(),
        source=source,
    )


# FR-12 — komponentga bog'langan tavsiya matnlari.
RECOMMENDATION_TEXTS = {
    Component.MOT.value: (
        "Kasbiy motivatsiyani mustahkamlang",
        "Har kuni 15 daqiqalik rivojlanish topshirig'ini bajaring va \"Mening maqsadim\" "
        "bo'limida bitta aniq, o'lchanadigan maqsad belgilang. Motivatsiya niyatdan emas, "
        "muntazam kichik harakatdan o'sadi.",
    ),
    Component.COG.value: (
        "Kasbiy bilim bazasini kengaytiring",
        "\"BioBilim\" bo'limida o'zlashtirilmagan mavzularga qayting. Har bir darsdan keyingi "
        "mustahkamlash testida 70 % dan yuqori natijaga erishing.",
    ),
    Component.ACT.value: (
        "Dars loyihalash ko'nikmasini mashq qiling",
        "\"Men — o'qituvchi\" bo'limidagi pedagogik keyslarni yeching va dars loyihasi "
        "konstruktorida kamida 3 ta to'liq fragment ishlab chiqing.",
    ),
    Component.REF.value: (
        "Refleksiv ko'nikmani rivojlantiring",
        "Har bir topshiriqdan keyin 4 ta savolga qisqa emas, dalilga asoslangan javob yozing: "
        "nima qildingiz, nima ish bermadi va keyingi safar aniq nimani o'zgartirasiz.",
    ),
    Component.CRE.value: (
        "Ijodiy yechim yaratishni mashq qiling",
        "\"Kreativ o'qituvchi\" bo'limida bitta mavzuni kamida ikki xil noodatiy usulda "
        "tushuntirib ko'ring va ularni bir-biri bilan solishtiring.",
    ),
}


def build_recommendations(user, measurement, limit=2):
    """FR-12 — eng zaif ikki komponent bo'yicha tavsiya yaratadi."""
    Recommendation.objects.filter(user=user, is_active=True).update(is_active=False)
    scores = measurement.as_dict()
    weakest = sorted(scores.items(), key=lambda item: item[1])[:limit]
    created = []
    for component, value in weakest:
        title, body = RECOMMENDATION_TEXTS[component]
        created.append(
            Recommendation.objects.create(
                user=user,
                measurement=measurement,
                component=component,
                title=title,
                body=f"Joriy daraja: {value:.0f} % ({level_for(value)[1]}). {body}",
            )
        )
    return created


def result_context(measurement):
    """FR-10 — natija sahifasi uchun ma'lumot."""
    scores = measurement.as_dict()
    rows = []
    for component in Component.values:
        value = scores[component]
        code, name, wash, step, hint = level_for(value)
        rows.append(
            {
                "code": component,
                "label": Component(component).label,
                "description": COMPONENT_DESCRIPTIONS[Component(component)],
                "value": round(value, 1),
                "level_name": name,
                "wash": wash,
                "step": step,
                "hint": hint,
            }
        )
    strongest = max(rows, key=lambda r: r["value"])
    weakest = min(rows, key=lambda r: r["value"])
    return {
        "measurement": measurement,
        "rows": rows,
        "strongest": strongest,
        "weakest": weakest,
        "level": level_for(measurement.sdi),
        "recommendations": measurement.recommendations.filter(is_active=True),
    }
