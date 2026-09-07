"""
Refleksiya sifatini baholash (FR-41).

Bu — HEURISTIK dastlabki baho: LLM emas, shaffof va tushuntirib beriladigan mezonlar.
Mentor uni qo'lda tuzatishi mumkin. Maqsad — shablon javoblarni ajratish va
talabaga aniq nima yetishmayotganini ko'rsatish.

Mezonlar (har biri 0..100, teng vaznda):
  1. To'liqlik      — 4 savolga ham javob berilganmi, hajmi yetarlimi (FR-40).
  2. Aniqlik        — o'ziga oid aniq harakat/hodisa tilga olinganmi.
  3. Tahlil         — sabab-oqibat bog'lanishi bormi ("chunki", "shuning uchun"...).
  4. Rejaviylik     — keyingi qadam aniq aytilganmi.
"""

import re

from .models import MIN_ANSWER_LENGTH

# Sabab-oqibat va tahlil markerlari.
ANALYSIS_MARKERS = [
    "chunki", "shuning uchun", "sababi", "natijada", "shu bois", "demak",
    "shu sababli", "buning sababi", "bog'liq", "ta'sir", "solishtir",
]

# Rejaviylik markerlari.
PLAN_MARKERS = [
    "keyingi", "ertaga", "rejalashtir", "qilaman", "o'rganaman", "sinab ko'raman",
    "boshlayman", "tayyorlayman", "qo'llayman", "yozaman", "takrorlayman", "kelgusi",
]

# Aniqlik markerlari — o'ziga oid faoliyat.
SPECIFIC_MARKERS = [
    "men ", "o'zim", "darsda", "topshiriq", "tajriba", "o'quvchi", "metod",
    "mavzu", "sinf", "loyiha", "vaziyat",
]

# Shablon / bo'sh javob belgilari.
FILLER_PATTERNS = [
    r"^\s*(ha|yo'q|yaxshi|zo'r|bilmadim|hammasi yaxshi|rahmat)\s*[.!]?\s*$",
    r"^\s*(-{1,}|\.{1,}|\?+)\s*$",
]


def _contains(text, markers):
    low = text.lower()
    return sum(1 for marker in markers if marker in low)


def _is_filler(text):
    return any(re.match(pattern, text.strip(), re.IGNORECASE) for pattern in FILLER_PATTERNS)


def _completeness(answers):
    """To'liqlik: har bir javob mavjud va yetarli hajmda."""
    if not answers:
        return 0.0
    per_answer_target = MIN_ANSWER_LENGTH / 4  # 4 savolga taqsimlangan minimal hajm
    points = []
    for answer in answers:
        text = (answer or "").strip()
        if not text or _is_filler(text):
            points.append(0.0)
            continue
        points.append(min(100.0, len(text) / per_answer_target * 100))
    return sum(points) / len(points)


def _specificity(text):
    hits = _contains(text, SPECIFIC_MARKERS)
    # 3 va undan ortiq marker — to'liq ball.
    return min(100.0, hits / 3 * 100)


def _analysis(text):
    hits = _contains(text, ANALYSIS_MARKERS)
    return min(100.0, hits / 2 * 100)


def _planning(text, q4):
    """Rejaviylik asosan 4-savolda kutiladi."""
    q4_text = (q4 or "").strip()
    if not q4_text or _is_filler(q4_text):
        return 0.0
    hits = _contains(q4_text, PLAN_MARKERS) or _contains(text, PLAN_MARKERS)
    base = min(100.0, hits / 2 * 100)
    if len(q4_text) < MIN_ANSWER_LENGTH / 4:
        base *= 0.6
    return base


def score_reflection(entry):
    """
    Refleksiyaning sifat balini (0..100) va tafsilotini qaytaradi.

    Natija `entry.quality_score` va `entry.quality_detail` ga yoziladi.
    """
    answers = [a for a in entry.answers]
    joined = " ".join(filter(None, answers + [entry.free_text]))

    detail = {
        "completeness": round(_completeness(answers) if entry.kind != entry.Kind.FREE
                              else min(100.0, len(entry.free_text.strip()) / MIN_ANSWER_LENGTH * 100), 1),
        "specificity": round(_specificity(joined), 1),
        "analysis": round(_analysis(joined), 1),
        "planning": round(_planning(joined, entry.q4), 1),
    }
    if entry.kind == entry.Kind.FREE:
        # Erkin yozuvda 4-savol yo'q — rejaviylik mezoni chiqarib tashlanadi.
        detail.pop("planning")

    score = round(sum(detail.values()) / len(detail), 1)
    detail["hints"] = build_hints(detail)
    return score, detail


HINT_TEXTS = {
    "completeness": "Javoblaringizni kengaytiring — har bir savolga kamida 2-3 to'liq jumla yozing.",
    "specificity": "Aniq misol keltiring: qaysi topshiriq, qaysi mavzu, qanday vaziyat edi.",
    "analysis": "Sababini tushuntiring: nima uchun aynan shunday bo'ldi? \"chunki\", \"natijada\" so'zlari yordam beradi.",
    "planning": "Keyingi qadamni aniq yozing: ertaga/keyingi darsda aynan nimani boshqacha qilasiz.",
}


def build_hints(detail, threshold=60):
    return [HINT_TEXTS[key] for key, value in detail.items()
            if key in HINT_TEXTS and isinstance(value, (int, float)) and value < threshold]


def save_with_score(entry):
    """Sifatni hisoblab saqlaydi va REF komponentini yangilaydi."""
    score, detail = score_reflection(entry)
    entry.quality_score = score
    entry.quality_detail = detail
    entry.save(update_fields=["quality_score", "quality_detail", "updated_at"])

    from progress.models import ActivityLog
    from progress.services import log_activity, recompute

    log_activity(entry.user, ActivityLog.Action.REFLECTION, object_ref=f"reflection:{entry.pk}")
    recompute(entry.user)

    from gamification.services import evaluate_badges

    evaluate_badges(entry.user)
    return entry
