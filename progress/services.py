"""
Rivojlanish hisoblash yadrosi.

Bu modul TZ'ning eng muhim ilmiy qismini amalga oshiradi:
  • komponent ballarini diagnostika + amaliyot aralashmasidan hisoblash;
  • SDI ni SR-04 formulasi bo'yicha chiqarish;
  • FR-67 — individual traektoriyani qayta hisoblash;
  • FR-46, FR-52 — faollik va muntazamlik.
"""

from datetime import timedelta

from django.db.models import Avg, Count
from django.utils import timezone

from core.enums import Component, compute_sdi, level_for

from .models import ActivityLog, ComponentScore, DailyTask, ProgressSnapshot, Streak

# Joriy ball = diagnostika × 0.4 + amaliyot × 0.6.
# Amaliyot ma'lumoti bo'lmasa — 100 % diagnostika, va aksincha.
DIAGNOSTIC_WEIGHT = 0.4
PRACTICE_WEIGHT = 0.6

# FR-67 — traektoriya shu qadar ish bajarilgach qayta hisoblanadi.
RECOMPUTE_EVERY_N_SUBMISSIONS = 10

# MOT komponentida faollikning ulushi (muntazam ishlash = motivatsiya ko'rsatkichi).
ENGAGEMENT_SHARE_IN_MOT = 0.5
ENGAGEMENT_TARGET_DAYS = 20  # 30 kunda 20 faol kun = 100 %

# Interfeysdagi ikonka — har bir kanal o'z belgisiga ega bo'lsin.
COMPONENT_ICONS = {
    "MOT": "flame", "COG": "book", "ACT": "clipboard", "REF": "pen", "CRE": "spark",
}


# ---------------------------------------------------------------- diagnostika

def diagnostic_scores(user):
    """Oxirgi yakunlangan urinishlardan komponent ballari (0..100)."""
    from diagnostics.models import Attempt

    result = {}
    attempts = (
        Attempt.objects.filter(user=user, status=Attempt.Status.FINISHED)
        .order_by("finished_at")
    )
    for attempt in attempts:
        for component, value in (attempt.scores or {}).items():
            if component in Component.values and value is not None:
                result[component] = float(value)  # keyingisi oldingisini almashtiradi
    return result


# ------------------------------------------------------------------ amaliyot

def practice_scores(user):
    """
    Bajarilgan ishlardan komponent ballari.

    ACT/CRE/COG — topshiriq natijalari; REF — refleksiya sifati;
    COG — qo'shimcha ravishda dars testlari; MOT — faollik indeksi.
    """
    from assignments.models import Submission
    from content.models import LessonProgress
    from reflection.models import ReflectionEntry

    scores = {}
    counts = {}

    graded = (
        Submission.objects.filter(
            student=user,
            status__in=[Submission.Status.SUBMITTED, Submission.Status.GRADED],
        )
        .select_related("assignment")
    )
    buckets = {}
    for submission in graded:
        percent = submission.final_percent
        if percent is None:
            continue
        buckets.setdefault(submission.assignment.component, []).append(percent)

    for component, values in buckets.items():
        scores[component] = sum(values) / len(values)
        counts[component] = len(values)

    # COG — dars testlari bilan boyitiladi.
    lesson_avg = LessonProgress.objects.filter(user=user, score__isnull=False).aggregate(
        avg=Avg("score"), n=Count("id")
    )
    if lesson_avg["n"]:
        existing = scores.get(Component.COG.value)
        if existing is None:
            scores[Component.COG.value] = lesson_avg["avg"]
        else:
            scores[Component.COG.value] = (existing + lesson_avg["avg"]) / 2
        counts[Component.COG.value] = counts.get(Component.COG.value, 0) + lesson_avg["n"]

    # REF — refleksiya sifati (FR-41).
    ref_avg = ReflectionEntry.objects.filter(user=user, quality_score__isnull=False).aggregate(
        avg=Avg("quality_score"), n=Count("id")
    )
    if ref_avg["n"]:
        existing = scores.get(Component.REF.value)
        if existing is None:
            scores[Component.REF.value] = ref_avg["avg"]
        else:
            scores[Component.REF.value] = (existing + ref_avg["avg"]) / 2
        counts[Component.REF.value] = counts.get(Component.REF.value, 0) + ref_avg["n"]

    # MOT — faollik indeksi bilan aralashtiriladi.
    engagement = engagement_index(user)
    if engagement is not None:
        existing = scores.get(Component.MOT.value)
        if existing is None:
            scores[Component.MOT.value] = engagement
        else:
            scores[Component.MOT.value] = (
                existing * (1 - ENGAGEMENT_SHARE_IN_MOT) + engagement * ENGAGEMENT_SHARE_IN_MOT
            )
        counts[Component.MOT.value] = counts.get(Component.MOT.value, 0) + 1

    return scores, counts


def engagement_index(user):
    """Oxirgi 30 kundagi faol kunlar ulushi (0..100). Faollik yo'q bo'lsa — None."""
    since = timezone.now() - timedelta(days=30)
    days = (
        ActivityLog.objects.filter(user=user, created_at__gte=since)
        .dates("created_at", "day")
        .count()
    )
    if days == 0:
        return None
    return min(100.0, days / ENGAGEMENT_TARGET_DAYS * 100)


# ------------------------------------------------------------- asosiy hisob

def blend(diagnostic, practice):
    """Ikki manbani aralashtirish; biri yo'q bo'lsa — ikkinchisi to'liq oladi."""
    if diagnostic is None and practice is None:
        return None, None, None
    if diagnostic is None:
        return round(practice, 2), None, round(practice, 2)
    if practice is None:
        return round(diagnostic, 2), round(diagnostic, 2), None
    value = diagnostic * DIAGNOSTIC_WEIGHT + practice * PRACTICE_WEIGHT
    return round(value, 2), round(diagnostic, 2), round(practice, 2)


def recompute(user, snapshot=True):
    """
    Barcha komponent ballarini qayta hisoblaydi va saqlaydi.

    Qaytaradi: {"MOT": 62.5, ..., "SDI": 64.1}
    """
    diagnostic = diagnostic_scores(user)
    practice, counts = practice_scores(user)
    stored = {row.component: row for row in ComponentScore.objects.filter(user=user)}

    values = {}
    for component in Component.values:
        value, diag_part, prac_part = blend(diagnostic.get(component), practice.get(component))
        if value is None:
            # Bu komponent bo'yicha yangi ma'lumot yo'q — qayta hisoblash mavjud
            # ko'rsatkichni O'CHIRMAYDI (masalan, o'lchov import qilingan holat).
            existing = stored.get(component)
            values[component] = existing.value if existing else 0.0
            continue

        values[component] = value
        ComponentScore.objects.update_or_create(
            user=user,
            component=component,
            defaults={
                "value": value,
                "diagnostic_part": diag_part,
                "practice_part": prac_part,
                "sample_size": counts.get(component, 0),
                "computed_at": timezone.now(),
            },
        )

    from diagnostics.models import ScoringWeights

    weights = ScoringWeights.active_weights()
    sdi = compute_sdi(values, weights)

    if snapshot:
        ProgressSnapshot.objects.update_or_create(
            user=user,
            date=timezone.localdate(),
            defaults={
                "mot": values[Component.MOT.value],
                "cog": values[Component.COG.value],
                "act": values[Component.ACT.value],
                "ref": values[Component.REF.value],
                "cre": values[Component.CRE.value],
                "sdi": sdi,
            },
        )

    result = dict(values)
    result["SDI"] = sdi
    return result


def current_scores(user):
    """Saqlangan joriy ballar (hisoblamasdan o'qish)."""
    rows = ComponentScore.objects.filter(user=user)
    scores = {row.component: row.value for row in rows}
    return {component: scores.get(component, 0.0) for component in Component.values}


def current_sdi(user):
    """Joriy SDI; hech qanday ball yo'q bo'lsa — None."""
    if not ComponentScore.objects.filter(user=user).exists():
        return None
    from diagnostics.models import ScoringWeights

    return compute_sdi(current_scores(user), ScoringWeights.active_weights())


def weakest_components(user, limit=2):
    """FR-12 / FR-67 — eng zaif komponentlar (traektoriya shularga yo'naltiriladi)."""
    scores = current_scores(user)
    ordered = sorted(scores.items(), key=lambda item: item[1])
    return [component for component, _ in ordered[:limit]]


def recommended_assignments(user, limit=3):
    """FR-67 — zaif komponentlarga mos, hali bajarilmagan topshiriqlar navbati."""
    from assignments.models import Assignment, Submission

    done_ids = Submission.objects.filter(student=user).values_list("assignment_id", flat=True)
    weak = weakest_components(user)
    queryset = Assignment.objects.filter(is_active=True).exclude(id__in=done_ids)
    primary = list(queryset.filter(component__in=weak).order_by("difficulty")[:limit])
    if len(primary) < limit:
        extra = queryset.exclude(id__in=[a.id for a in primary]).order_by("difficulty")
        primary += list(extra[: limit - len(primary)])
    return primary


# ------------------------------------------------------- faollik va streak

def log_activity(user, action, object_ref="", points=1, **meta):
    """FR-46 — faollik yozuvi + streak yangilanishi."""
    entry = ActivityLog.objects.create(
        user=user, action=action, object_ref=str(object_ref)[:200], points=points, meta=meta
    )
    touch_streak(user)
    return entry


def touch_streak(user):
    """FR-52 — ketma-ket faol kunlarni yangilaydi."""
    today = timezone.localdate()
    streak, _ = Streak.objects.get_or_create(user=user)
    if streak.last_active_date == today:
        return streak
    if streak.last_active_date == today - timedelta(days=1):
        streak.current += 1
    else:
        streak.current = 1
    streak.longest = max(streak.longest, streak.current)
    streak.last_active_date = today
    streak.total_active_days += 1
    streak.save()
    return streak


# ------------------------------------------------------------- kunlik vazifa

DAILY_TEMPLATES = [
    (Component.MOT, "Kasbiy motivatsiya",
     "Bugun o'zingizga ta'sir qilgan bitta o'qituvchini eslang va uning qaysi sifati "
     "sizga namuna bo'lishini 3-4 jumlada yozing."),
    (Component.COG, "Bitta biologik tushuncha",
     "Maktab biologiya darsligidan bitta murakkab tushunchani tanlang va uni "
     "7-sinf o'quvchisi tushunadigan tilda qayta bayon qiling."),
    (Component.COG, "Ilmiy yangilik",
     "Biologiya bo'yicha bitta yangi ilmiy xabar o'qing va uni darsning qaysi "
     "mavzusiga bog'lash mumkinligini yozing."),
    (Component.ACT, "Bitta yangi metod",
     "Bugun bitta faol ta'lim metodini o'rganing (masalan: 'Insert', 'Klaster', "
     "'Baliq skeleti') va uni qaysi mavzuda qo'llashingizni yozing."),
    (Component.ACT, "Mikro-vaziyat tahlili",
     "Tasavvur qiling: dars o'rtasida ikki o'quvchi bahslashib qoldi. "
     "Darsni buzmasdan qanday yo'l tutasiz?"),
    (Component.CRE, "Noodatiy tushuntirish",
     "Bugungi biologik jarayonni (fotosintez, nafas olish, osmos) kundalik hayotdagi "
     "metafora orqali tushuntiring."),
    (Component.CRE, "Bitta yangi topshiriq",
     "O'zingiz tanlagan mavzuga 'Yarataman' darajasidagi bitta topshiriq o'ylab toping."),
    (Component.REF, "Kunlik refleksiya",
     "Bugun kasbiy jihatdan nimani o'rgandingiz va ertaga nimani boshqacha qilasiz?"),
]


def daily_task_for(user, date=None):
    """FR-52 — kunning mikro-topshirig'i (bir kunga bitta, barqaror tanlov)."""
    date = date or timezone.localdate()
    task = DailyTask.objects.filter(user=user, date=date).first()
    if task:
        return task
    index = (user.pk + date.toordinal()) % len(DAILY_TEMPLATES)
    component, title, description = DAILY_TEMPLATES[index]
    return DailyTask.objects.create(
        user=user, date=date, title=title, description=description, component=component
    )


# ------------------------------------------------------------------- xulosa

def dynamics_summary(user):
    """FR-47 — avtomatik matnli xulosa (eng katta o'sish haqida)."""
    from diagnostics.models import Measurement

    measurements = list(
        Measurement.objects.filter(user=user, is_void=False).order_by("created_at")
    )
    if len(measurements) < 2:
        snapshots = list(ProgressSnapshot.objects.filter(user=user).order_by("date"))
        if len(snapshots) < 2:
            return None
        first, last = snapshots[0], snapshots[-1]
        delta = round(last.sdi - first.sdi, 1)
        days = (last.date - first.date).days or 1
        if abs(delta) < 0.5:
            return f"So'nggi {days} kunda SDI ko'rsatkichingiz barqaror ({last.sdi:.0f} %)."
        yo = "o'sdi" if delta > 0 else "pasaydi"
        return f"So'nggi {days} kunda umumiy SDI ko'rsatkichingiz {abs(delta):.1f} % {yo}."

    first, last = measurements[0], measurements[-1]
    diffs = {
        component: last.as_dict()[component] - first.as_dict()[component]
        for component in Component.values
    }
    best = max(diffs, key=diffs.get)
    label = Component(best).label
    delta = round(diffs[best], 1)
    period = (last.created_at - first.created_at).days or 1
    months = max(1, round(period / 30))
    if delta <= 0:
        return (
            f"{first.get_cut_display()} dan {last.get_cut_display()} gacha SDI "
            f"{first.sdi:.0f} % → {last.sdi:.0f} %. Faollikni oshirish tavsiya etiladi."
        )
    return (
        f"Sizning \"{label}\" ko'rsatkichingiz {months} oyda +{delta:.0f} % o'sdi. "
        f"Umumiy SDI: {first.sdi:.0f} % → {last.sdi:.0f} %."
    )


def dashboard_context(user):
    """Dashboard va monitoring sahifalari uchun umumiy ma'lumot to'plami."""
    scores = current_scores(user)
    sdi = current_sdi(user)
    code, name, wash, step, hint = level_for(sdi or 0)
    return {
        "scores": scores,
        "scores_list": [
            {
                "code": component,
                "label": Component(component).label,
                "value": round(scores[component], 1),
                "level": level_for(scores[component]),
                "icon": COMPONENT_ICONS[component],
            }
            for component in Component.values
        ],
        "sdi": sdi,
        "level": {"code": code, "name": name, "wash": wash, "step": step, "hint": hint},
        "summary": dynamics_summary(user),
        "streak": Streak.objects.filter(user=user).first(),
        "daily_task": daily_task_for(user),
        "recommended": recommended_assignments(user),
    }

def growth_series(user, max_points=14):
    """
    Oʻsish grafigi uchun qatorlar — bu platformaning asosiy vizual obyekti.

    Manba: muzlatilgan kesim oʻlchovlari (SR-06) va kunlik kesmalar birlashtiriladi,
    sanaga koʻra tartiblanadi. Nuqta koʻp boʻlsa, tekis oraliqda siyraklashtiriladi.

    Qaytaradi: {"labels": [...], "channels": {"MOT": [...], ...}, "sdi": [...],
                "points": n, "delta": {"MOT": +12.0, ...}}
    """
    from diagnostics.models import Measurement

    points = []
    for m in Measurement.objects.filter(user=user, is_void=False).order_by("created_at"):
        points.append((m.created_at.date(), m.as_dict(), m.sdi, m.get_cut_display()))
    for snap in ProgressSnapshot.objects.filter(user=user).order_by("date"):
        points.append((snap.date, snap.as_dict(), snap.sdi, None))

    if not points:
        return None

    points.sort(key=lambda row: row[0])
    # Bir kunda bir nechta yozuv boʻlsa — oxirgisi qoladi.
    unique = {}
    for date, scores, sdi, mark in points:
        unique[date] = (scores, sdi, mark or unique.get(date, (None, None, None))[2])
    ordered = [(d, *unique[d]) for d in sorted(unique)]

    if len(ordered) > max_points:
        step = (len(ordered) - 1) / (max_points - 1)
        keep = {round(i * step) for i in range(max_points)}
        keep.add(len(ordered) - 1)
        ordered = [row for i, row in enumerate(ordered) if i in keep]

    labels = [d.strftime("%d.%m") for d, _, _, _ in ordered]
    channels = {
        component: [round(scores[component], 1) for _, scores, _, _ in ordered]
        for component in Component.values
    }
    sdi_line = [round(sdi, 1) for _, _, sdi, _ in ordered]
    delta = {
        component: round(values[-1] - values[0], 1) if len(values) > 1 else None
        for component, values in channels.items()
    }
    return {
        "labels": labels,
        "marks": [mark for _, _, _, mark in ordered],
        "channels": channels,
        "sdi": sdi_line,
        "points": len(ordered),
        "delta": delta,
        "sdi_delta": round(sdi_line[-1] - sdi_line[0], 1) if len(sdi_line) > 1 else None,
    }


def biggest_movers(user, limit=2):
    """Eng koʻp oʻsgan kanallar — grafik ostidagi bitta jumla uchun."""
    series = growth_series(user)
    if not series:
        return []
    moved = [
        (component, value) for component, value in series["delta"].items()
        if value is not None and abs(value) >= 0.5
    ]
    moved.sort(key=lambda row: -abs(row[1]))
    return [
        {"code": code, "label": Component(code).label, "delta": value}
        for code, value in moved[:limit]
    ]

def weakest_reading(user):
    """
    Eng past kanal — hero uchun bitta aniq jumla.

    Tarix boʻlmaganda ham foydalanuvchiga nima qilish kerakligini aytadi.
    """
    scores = current_scores(user)
    if not any(scores.values()):
        return None
    code = min(scores, key=scores.get)
    return {"code": code, "label": Component(code).label, "value": round(scores[code])}
