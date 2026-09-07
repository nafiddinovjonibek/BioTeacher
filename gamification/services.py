"""
Nishonlarni avtomatik berish (FR-49, FR-50).

Metrikalar shaffof: har biri oddiy so'rov. Yangi metrika qo'shish uchun
`BadgeRule.Metric` ga qiymat va bu yerga funksiya qo'shiladi.
"""

from django.db.models import Count

from core.enums import Module

from .models import BadgeRule, UserBadge


def _submissions(user, **filters):
    from assignments.models import Submission

    return Submission.objects.filter(
        student=user,
        status__in=[Submission.Status.SUBMITTED, Submission.Status.GRADED],
        **filters,
    ).count()


def metric_submissions_graded(user):
    from assignments.models import Submission

    return Submission.objects.filter(student=user, status=Submission.Status.GRADED).count()


def metric_lab_submissions(user):
    return _submissions(user, assignment__module=Module.LAB)


def metric_lesson_plans(user):
    from assignments.models import Assignment

    return _submissions(user, assignment__kind=Assignment.Kind.LESSON_PLAN)


def metric_creative_works(user):
    return _submissions(user, assignment__module=Module.CREATIVE)


def metric_digital_works(user):
    return _submissions(user, assignment__module=Module.DIGITAL)


def metric_reflections(user):
    from reflection.models import ReflectionEntry

    return ReflectionEntry.objects.filter(user=user).count()


def metric_lessons_passed(user):
    from content.models import LessonProgress

    return LessonProgress.objects.filter(user=user, status=LessonProgress.Status.PASSED).count()


def metric_streak(user):
    from progress.models import Streak

    streak = Streak.objects.filter(user=user).first()
    return streak.longest if streak else 0


def metric_goals_done(user):
    from goals.models import Goal

    return Goal.objects.filter(user=user, status=Goal.Status.DONE).count()


def metric_sdi(user):
    from progress.services import current_sdi

    return current_sdi(user) or 0


def metric_sdi_growth(user):
    """SR-07 — taqqoslash faqat o'z oldingi natijasi bilan."""
    from diagnostics.models import Measurement

    measurements = list(
        Measurement.objects.filter(user=user, is_void=False).order_by("created_at")
    )
    if len(measurements) < 2:
        from progress.models import ProgressSnapshot

        snapshots = list(ProgressSnapshot.objects.filter(user=user).order_by("date"))
        if len(snapshots) < 2:
            return 0
        return snapshots[-1].sdi - snapshots[0].sdi
    return measurements[-1].sdi - measurements[0].sdi


METRICS = {
    BadgeRule.Metric.SUBMISSIONS_GRADED: metric_submissions_graded,
    BadgeRule.Metric.LAB_SUBMISSIONS: metric_lab_submissions,
    BadgeRule.Metric.LESSON_PLANS: metric_lesson_plans,
    BadgeRule.Metric.CREATIVE_WORKS: metric_creative_works,
    BadgeRule.Metric.DIGITAL_WORKS: metric_digital_works,
    BadgeRule.Metric.REFLECTIONS: metric_reflections,
    BadgeRule.Metric.LESSONS_PASSED: metric_lessons_passed,
    BadgeRule.Metric.STREAK: metric_streak,
    BadgeRule.Metric.GOALS_DONE: metric_goals_done,
    BadgeRule.Metric.SDI: metric_sdi,
    BadgeRule.Metric.SDI_GROWTH: metric_sdi_growth,
}


def evaluate_badges(user):
    """Barcha qoidalarni tekshiradi va yangi nishonlarni beradi."""
    owned = set(UserBadge.objects.filter(user=user).values_list("badge_id", flat=True))
    rules = (
        BadgeRule.objects.filter(is_active=True, badge__is_active=True)
        .select_related("badge")
        .exclude(badge_id__in=owned)
    )

    # Bitta nishonda bir nechta qoida bo'lsa — HAMMASI bajarilishi kerak.
    by_badge = {}
    for rule in rules:
        by_badge.setdefault(rule.badge, []).append(rule)

    awarded = []
    for badge, badge_rules in by_badge.items():
        reasons = []
        satisfied = True
        for rule in badge_rules:
            metric_fn = METRICS.get(rule.metric)
            if metric_fn is None:
                satisfied = False
                break
            value = metric_fn(user) or 0
            if value < rule.threshold:
                satisfied = False
                break
            reasons.append(f"{rule.get_metric_display()}: {value:g} ≥ {rule.threshold:g}")
        if satisfied and reasons:
            UserBadge.objects.get_or_create(
                user=user, badge=badge, defaults={"reason": "; ".join(reasons)[:250]}
            )
            awarded.append(badge)

    if awarded:
        from notifications.models import NotificationType
        from notifications.services import notify
        from progress.models import ActivityLog
        from progress.services import log_activity

        for badge in awarded:
            notify(
                user,
                NotificationType.BADGE,
                title=f"Yangi nishon: {badge.emoji} {badge.title}",
                body=badge.description or badge.how_to_earn,
                url="/yutuqlar/",
            )
            log_activity(user, ActivityLog.Action.BADGE, object_ref=badge.code)
    return awarded


def badge_board(user):
    """
    FR-49/FR-51 — talabaning nishonlar taxtasi.

    Ochiq reyting YO'Q: faqat o'zining olgan va olmagan nishonlari ko'rsatiladi.
    """
    from .models import Badge

    owned = {ub.badge_id: ub for ub in UserBadge.objects.filter(user=user).select_related("badge")}
    rows = []
    for badge in Badge.objects.filter(is_active=True).prefetch_related("rules"):
        earned = owned.get(badge.id)
        progress = None
        rules = list(badge.rules.filter(is_active=True))
        if rules and not earned:
            ratios = []
            for rule in rules:
                metric_fn = METRICS.get(rule.metric)
                if metric_fn is None or rule.threshold <= 0:
                    continue
                ratios.append(min(1.0, (metric_fn(user) or 0) / rule.threshold))
            if ratios:
                progress = round(min(ratios) * 100)
        rows.append({"badge": badge, "earned": earned, "progress": progress})
    return rows
