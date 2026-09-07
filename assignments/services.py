"""
Topshiriqlarni baholash servislari (FR-25, FR-31, FR-55).

Rubrika bo'yicha ball 0..100 foizga aylantiriladi:
    percent = Σ(ball_i × vazn_i) / Σ(max_i × vazn_i) × 100
"""

from django.db import transaction
from django.utils import timezone

from .models import Score, Submission


def rubric_percent(submission, scorer):
    """Berilgan baholovchi (SELF/MENTOR) bo'yicha rubrika foizi. Ball yo'q bo'lsa — None."""
    scores = list(
        submission.scores.filter(scorer=scorer).select_related("criterion")
    )
    if not scores:
        return None
    earned = sum(s.value * s.criterion.weight for s in scores)
    possible = sum(s.criterion.max_score * s.criterion.weight for s in scores)
    if possible <= 0:
        return None
    return round(earned / possible * 100, 2)


@transaction.atomic
def apply_scores(submission, scorer, values, author=None, comments=None):
    """
    Mezon → ball lug'atini saqlaydi va yakuniy foizni yangilaydi.

    `values`  — {criterion_id: ball}
    `comments`— {criterion_id: izoh}
    """
    comments = comments or {}
    criteria = {c.id: c for c in submission.assignment.rubric.criteria.all()}
    for criterion_id, value in values.items():
        criterion = criteria.get(int(criterion_id))
        if criterion is None:
            continue
        bounded = max(0, min(criterion.max_score, float(value)))
        Score.objects.update_or_create(
            submission=submission,
            criterion=criterion,
            scorer=scorer,
            defaults={
                "value": bounded,
                "comment": comments.get(str(criterion_id), "")[:2000],
                "author": author,
            },
        )

    percent = rubric_percent(submission, scorer)
    if scorer == Score.Scorer.SELF:
        submission.self_percent = percent
        if submission.status == Submission.Status.DRAFT:
            submission.status = Submission.Status.SELF_ASSESSED
        submission.save(update_fields=["self_percent", "status", "updated_at"])
    else:
        submission.mentor_percent = percent
        submission.status = Submission.Status.GRADED
        submission.graded_at = timezone.now()
        submission.graded_by = author
        submission.save(
            update_fields=["mentor_percent", "status", "graded_at", "graded_by", "updated_at"]
        )
    return percent


def finalize_submission(submission):
    """Ish yuborilganda: status, faollik, ball qayta hisobi, nishonlar."""
    submission.mark_submitted()

    from progress.models import ActivityLog
    from progress.services import log_activity, recompute

    log_activity(
        submission.student,
        ActivityLog.Action.SUBMISSION,
        object_ref=submission.assignment.title,
        points=2,
        module=submission.assignment.module,
    )
    recompute(submission.student)

    from gamification.services import evaluate_badges

    evaluate_badges(submission.student)
    return submission


def notify_graded(submission):
    """FR-64/FR-65 — baho qo'yilgani haqida xabar."""
    from notifications.models import NotificationType
    from notifications.services import notify

    percent = submission.mentor_percent or 0
    notify(
        submission.student,
        NotificationType.GRADED,
        title=f"\"{submission.assignment.title}\" ishingiz baholandi",
        body=f"Mentor bahosi: {percent:.0f} %. Izohni ish sahifasida ko'ring.",
        url=f"/topshiriqlar/ish/{submission.pk}/",
    )


def assessment_gap_stats(user):
    """FR-25 — baholash adekvatligi: o'rtacha farq va uning talqini."""
    gaps = [
        s.assessment_gap
        for s in Submission.objects.filter(student=user, status=Submission.Status.GRADED)
        if s.assessment_gap is not None
    ]
    if not gaps:
        return None
    average = round(sum(gaps) / len(gaps), 1)
    if abs(average) <= 5:
        verdict = "O'zingizni adekvat baholaysiz — bu kuchli refleksiv ko'nikma belgisi."
    elif average > 5:
        verdict = "O'zingizni mentordan yuqori baholaysiz. Rubrika mezonlarini diqqat bilan o'qing."
    else:
        verdict = "O'zingizni mentordan past baholaysiz. Ishingizga ishonch bilan qarang."
    return {"average": average, "count": len(gaps), "verdict": verdict}
