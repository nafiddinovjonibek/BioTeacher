"""
Tadqiqot moduli servislari (FR-59..FR-62).

Eksport NFR-17 ga muvofiq anonim: F.I.Sh. o'rniga barqaror `respondent_id`.
Statistika — tashqi kutubxonasiz (dissertatsiyaga t-mezon/χ² hisoblash uchun
kirish ma'lumoti tayyorlanadi).
"""

import csv
import io
import math

from core.enums import COMPONENT_ORDER, CUT_ORDER, Component, Cut, StudyArm

# FR-59 — eksport ustunlari qat'iy shu tartibda.
EXPORT_COLUMNS = [
    "respondent_id", "group", "cut",
    "MOT", "COG", "ACT", "REF", "CRE", "SDI",
    "date",
]


def measurement_rows(cuts=None, arms=None, include_void=False):
    """Eksport uchun qatorlar (dict ro'yxati)."""
    from diagnostics.models import Measurement

    queryset = Measurement.objects.select_related("user__profile__group")
    if not include_void:
        queryset = queryset.filter(is_void=False)
    if cuts:
        queryset = queryset.filter(cut__in=cuts)

    rows = []
    for measurement in queryset.order_by("user_id", "created_at"):
        profile = getattr(measurement.user, "profile", None)
        if profile is None:
            continue
        arm = profile.study_arm
        if arms and arm not in arms:
            continue
        rows.append(
            {
                "respondent_id": profile.short_code(),
                "group": arm,
                "cut": measurement.cut,
                "MOT": round(measurement.mot, 2),
                "COG": round(measurement.cog, 2),
                "ACT": round(measurement.act, 2),
                "REF": round(measurement.ref, 2),
                "CRE": round(measurement.cre, 2),
                "SDI": round(measurement.sdi, 2),
                "date": measurement.created_at.strftime("%Y-%m-%d"),
            }
        )
    return rows


def to_csv(rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=EXPORT_COLUMNS, delimiter=";")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig")  # Excel uchun BOM


def to_xlsx(rows):
    """openpyxl mavjud bo'lmasa None qaytaradi — chaqiruvchi CSV'ga qaytadi."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font
    except ImportError:  # pragma: no cover
        return None

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Measurements"
    sheet.append(EXPORT_COLUMNS)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    for row in rows:
        sheet.append([row[column] for column in EXPORT_COLUMNS])
    for index, column in enumerate(EXPORT_COLUMNS, start=1):
        sheet.column_dimensions[sheet.cell(row=1, column=index).column_letter].width = (
            16 if column in {"respondent_id", "cut", "date"} else 10
        )
    sheet.freeze_panes = "A2"

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


# ------------------------------------------------------------- statistika

def describe(values):
    """FR-61 — n, M, SD (tanlanma), min, max."""
    values = [float(v) for v in values if v is not None]
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": 0.0, "sd": 0.0, "min": 0.0, "max": 0.0}
    mean = sum(values) / n
    if n > 1:
        variance = sum((v - mean) ** 2 for v in values) / (n - 1)
        sd = math.sqrt(variance)
    else:
        sd = 0.0
    return {
        "n": n,
        "mean": round(mean, 2),
        "sd": round(sd, 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
    }


def stats_table(rows=None):
    """
    FR-61/FR-62 — kesim × guruh × komponent kesimidagi tavsifiy statistika.

    Qaytadi: [{"cut": ..., "arm": ..., "component": ..., "n":..., "mean":..., ...}]
    """
    rows = measurement_rows() if rows is None else rows
    keys = [c.value for c in COMPONENT_ORDER] + ["SDI"]
    buckets = {}
    for row in rows:
        for key in keys:
            buckets.setdefault((row["cut"], row["group"], key), []).append(row[key])

    table = []
    for cut in CUT_ORDER:
        for arm in [StudyArm.EXPERIMENTAL, StudyArm.CONTROL, StudyArm.NONE]:
            for key in keys:
                values = buckets.get((cut.value, arm.value, key))
                if not values:
                    continue
                stats = describe(values)
                table.append(
                    {
                        "cut": cut.value,
                        "cut_label": cut.label,
                        "arm": arm.value,
                        "arm_label": arm.label,
                        "component": key,
                        "component_label": Component(key).label if key != "SDI" else "SDI",
                        **stats,
                    }
                )
    return table


def comparison_table(rows=None):
    """
    FR-62 — guruhlararo taqqoslash uchun tayyor jadval.

    Har bir komponent uchun: E va C guruhlarining boshlang'ich va yakuniy
    o'rtachalari hamda o'sish (Δ). t-mezon hisoblash uchun n va SD ham beriladi.
    """
    rows = measurement_rows() if rows is None else rows
    keys = [c.value for c in COMPONENT_ORDER] + ["SDI"]
    result = []
    for key in keys:
        entry = {"component": key,
                 "label": Component(key).label if key != "SDI" else "Umumiy SDI"}
        for arm in (StudyArm.EXPERIMENTAL, StudyArm.CONTROL):
            initial = describe(
                [r[key] for r in rows if r["group"] == arm.value and r["cut"] == Cut.INITIAL]
            )
            final = describe(
                [r[key] for r in rows if r["group"] == arm.value and r["cut"] == Cut.FINAL]
            )
            entry[arm.value] = {
                "initial": initial,
                "final": final,
                "delta": round(final["mean"] - initial["mean"], 2),
            }
        entry["delta_diff"] = round(
            entry[StudyArm.EXPERIMENTAL.value]["delta"] - entry[StudyArm.CONTROL.value]["delta"], 2
        )
        result.append(entry)
    return result


def independent_t(sample_a, sample_b):
    """
    Ikki bog'liqsiz tanlanma uchun Welch t-statistikasi va erkinlik darajasi.

    p-qiymat hisoblanmaydi — bu yerda maqsad dissertatsiyaga kiritish uchun
    tayyor kirish ma'lumotini berish (SPSS/Statistica'da yakunlanadi).
    """
    a, b = describe(sample_a), describe(sample_b)
    if a["n"] < 2 or b["n"] < 2:
        return None
    va, vb = a["sd"] ** 2 / a["n"], b["sd"] ** 2 / b["n"]
    denominator = math.sqrt(va + vb)
    if denominator == 0:
        return None
    t = (a["mean"] - b["mean"]) / denominator
    df_num = (va + vb) ** 2
    df_den = va**2 / (a["n"] - 1) + vb**2 / (b["n"] - 1)
    df = df_num / df_den if df_den else 0
    return {"t": round(t, 3), "df": round(df, 1), "a": a, "b": b}


def refresh_stat_summary():
    """Statistik keshni yangilaydi (StatSummary jadvali)."""
    from .models import StatSummary

    StatSummary.objects.all().delete()
    objects = [
        StatSummary(
            cut=row["cut"], arm=row["arm"], component=row["component"],
            n=row["n"], mean=row["mean"], sd=row["sd"],
            minimum=row["min"], maximum=row["max"],
        )
        for row in stats_table()
    ]
    StatSummary.objects.bulk_create(objects)
    return len(objects)
