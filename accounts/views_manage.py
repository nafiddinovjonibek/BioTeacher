"""
Admin boshqaruv paneli (TZ M12: FR-53..FR-57).

Faqat ADMIN roli kiradi: barcha o'qituvchilar ro'yxati, analitika, e'lon
va topshiriq tayinlash (NFR-12).
"""

import statistics as stats_lib

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from core.enums import Component, level_for

from .permissions import admin_required
from .services import learner_queryset, log_action

RISK_THRESHOLD = 50  # SDI shu qiymatdan past bo'lsa — foydalanuvchi xavf ostida (FR-56)


def _student_rows():
    """O'qituvchilar: SDI, daraja, oxirgi faollik, tekshirilmagan ishlar."""
    from assignments.models import Submission
    from progress.models import ActivityLog
    from progress.services import current_sdi

    rows = []
    for student in learner_queryset():
        sdi = current_sdi(student)
        last_activity = ActivityLog.objects.filter(user=student).order_by("-created_at").first()
        rows.append(
            {
                "student": student,
                "profile": getattr(student, "profile", None),
                "sdi": sdi,
                "level": level_for(sdi or 0),
                "last_activity": last_activity.created_at if last_activity else None,
                "pending": Submission.objects.filter(
                    student=student, status=Submission.Status.SUBMITTED
                ).count(),
                "at_risk": sdi is not None and sdi < RISK_THRESHOLD,
            }
        )
    return sorted(rows, key=lambda r: (r["sdi"] is None, r["sdi"] or 0))


@admin_required
def students(request):
    """FR-53 — o'qituvchilar ro'yxati."""
    rows = _student_rows()
    return render(
        request,
        "manage/students.html",
        {"rows": rows, "total": len(rows), "risk_threshold": RISK_THRESHOLD},
    )


@admin_required
def analytics(request):
    """FR-56 — analitika: o'rtacha, mediana, eng zaif komponent, xavf ostidagilar."""
    rows = _student_rows()

    from progress.services import current_scores

    component_values = {c: [] for c in Component.values}
    sdis = []
    for row in rows:
        if row["sdi"] is None:
            continue
        sdis.append(row["sdi"])
        scores = current_scores(row["student"])
        for component in Component.values:
            component_values[component].append(scores[component])

    def summarize(values):
        if not values:
            return None
        return {
            "n": len(values),
            "mean": round(sum(values) / len(values), 1),
            "median": round(stats_lib.median(values), 1),
            "min": round(min(values), 1),
            "max": round(max(values), 1),
        }

    components = []
    for component in Component.values:
        summary = summarize(component_values[component])
        if summary:
            components.append({"code": component, "label": Component(component).label, **summary})

    weakest = min(components, key=lambda c: c["mean"]) if components else None
    at_risk = [row for row in rows if row["at_risk"]]

    return render(
        request,
        "manage/analytics.html",
        {
            "sdi": summarize(sdis),
            "components": components,
            "weakest": weakest,
            "at_risk": at_risk,
            "rows": rows,
            "risk_threshold": RISK_THRESHOLD,
        },
    )


@admin_required
def student_card(request, user_id):
    """FR-53 — foydalanuvchi kartochkasi (monitoring sahifasiga yo'naltiradi)."""
    return redirect("progress:student", user_id=user_id)


@admin_required
def announce(request):
    """FR-57 — barcha o'qituvchilarga e'lon yoki topshiriq tayinlash."""
    from assignments.forms import AssignTaskForm
    from assignments.models import AssignedTask
    from notifications.models import NotificationType
    from notifications.services import notify_students

    task_form = AssignTaskForm(request.POST or None)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "announce":
            title = request.POST.get("title", "").strip()
            body = request.POST.get("body", "").strip()
            if not title:
                messages.error(request, "E'lon sarlavhasini kiriting.")
            else:
                created = notify_students(
                    NotificationType.SYSTEM, title=title, body=body, exclude=request.user
                )
                log_action(request, "announce.send", title)
                messages.success(request, f"E'lon {len(created)} ta o'qituvchiga yuborildi.")
                return redirect("manage:students")
        elif action == "assign" and task_form.is_valid():
            assignment = task_form.cleaned_data["assignment"]
            AssignedTask.objects.update_or_create(
                assignment=assignment,
                defaults={
                    "assigned_by": request.user,
                    "deadline": task_form.cleaned_data["deadline"],
                    "note": task_form.cleaned_data["note"],
                },
            )
            notify_students(
                NotificationType.NEW_ASSIGNMENT,
                title=f"Yangi topshiriq: {assignment.title}",
                body=task_form.cleaned_data["note"] or assignment.body[:300],
                url=f"/topshiriqlar/{assignment.slug}/",
                exclude=request.user,
            )
            log_action(request, "assignment.assign", assignment.slug)
            messages.success(request, "Topshiriq o'qituvchilarga tayinlandi.")
            return redirect("manage:students")

    return render(
        request,
        "manage/announce.html",
        {"task_form": task_form, "assigned": AssignedTask.objects.select_related("assignment")},
    )


# ------------------------------------------------------------ menyu tartibi

def _json_body(request):
    import json

    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def _back_to_menu(anchor=""):
    from django.urls import reverse

    return redirect(reverse("manage:menu") + (f"#{anchor}" if anchor else ""))


@admin_required
def menu(request):
    """Yon panel: bloklar, bandlar va ichki bandlar — qo'shish, o'chirish, nom va tartib."""
    from .menu import ADMIN, ICONS, TEACHER, active_sections, manage_cards, page_choices, page_defaults

    sections = active_sections()
    cards = manage_cards(sections)
    # «Fanlar» ro'yxatining ichi — alohida karta: tartibi va nomlari fanlarning o'zida.
    sections_card = {
        "code": "sections", "title": "«Fanlar» ichidagi ro‘yxat",
        "items": [{"key": str(s.pk), "label": s.title, "icon": s.icon_name} for s in sections],
    }
    forms = {c["form"]["key"]: dict(c["form"], group=card["code"])
             for card in cards for item in card["items"] for c in [item, *item["children"]]}
    return render(request, "manage/menu.html", {
        "teacher_groups": [c for c in cards if c["audience"] == TEACHER],
        "admin_groups": [c for c in cards if c["audience"] == ADMIN],
        "sections_card": sections_card,
        "page_choices": {TEACHER: page_choices(TEACHER, sections), ADMIN: page_choices(ADMIN)},
        "icons": ICONS,
        "menu_data": {"items": forms, "pages": page_defaults(sections)},
    })


@admin_required
def menu_reorder(request):
    """
    POST JSON:
    {"group": blok, "keys": [...]}      — blokdagi bandlar (boshqa blokdan olib kelingani ko'chadi);
    {"parent": band, "keys": [...]}     — ichki bandlar;
    {"group": "__groups__", "keys": [...]} — o'qituvchi menyusidagi bloklar.
    """
    from django.http import JsonResponse

    from .menu import save_children_order, save_group_order, save_order

    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST kerak"}, status=405)
    payload = _json_body(request)
    if payload is None or not isinstance(payload.get("keys"), list):
        return JsonResponse({"ok": False, "error": "noto'g'ri ma'lumot"}, status=400)
    keys = [str(k) for k in payload["keys"]]
    group, parent = payload.get("group"), payload.get("parent")
    if group == "__groups__":
        keys = save_group_order(keys)
    elif parent:
        keys = save_children_order(str(parent), keys)
    else:
        keys = save_order(str(group), keys)
    if keys is None:
        return JsonResponse({"ok": False, "error": "noto'g'ri guruh"}, status=400)
    log_action(request, "menu.reorder", parent or group, keys=keys)
    return JsonResponse({"ok": True, "keys": keys})


@admin_required
def menu_rename(request):
    """POST JSON {"kind": "item"|"group"|"section", "key": ..., "label": ...}."""
    from django.http import JsonResponse

    from content.models import Section

    from .menu import rename_group, rename_item

    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST kerak"}, status=405)
    payload = _json_body(request) or {}
    kind, key, label = payload.get("kind"), str(payload.get("key", "")), str(payload.get("label", ""))

    if kind == "item":
        result = rename_item(key, label)
    elif kind == "group":
        result = rename_group(key, label)
    elif kind == "section" and key.isdigit():
        label = label.strip()[:200]
        if not label:
            return JsonResponse({"ok": False, "error": "Fan nomi bo'sh bo'lmasin"}, status=400)
        section = Section.objects.filter(pk=int(key)).first()
        if section is None:
            return JsonResponse({"ok": False, "error": "Fan topilmadi"}, status=404)
        section.title = label
        section.save(update_fields=["title", "updated_at"])
        result = label
    else:
        result = None
    if result is None:
        return JsonResponse({"ok": False, "error": "noto'g'ri ma'lumot yoki bo'sh nom"}, status=400)
    log_action(request, "menu.rename", f"{kind}:{key}", label=result)
    return JsonResponse({"ok": True, "label": result})


@admin_required
@require_POST
def menu_group_add(request):
    from .menu import add_group

    group = add_group(request.POST.get("title", ""))
    log_action(request, "menu.group.add", group.key, title=group.title)
    messages.success(request, f"«{group.title}» bloki qo‘shildi. Endi unga band qo‘shing.")
    return _back_to_menu(f"g-{group.key}")


@admin_required
@require_POST
def menu_group_delete(request, group):
    from .menu import delete_group

    if not delete_group(group):
        messages.error(request, "Bu blokni o‘chirib bo‘lmaydi.")
        return _back_to_menu()
    log_action(request, "menu.group.delete", group)
    messages.success(request, "Blok bandlari bilan o‘chirildi.")
    return _back_to_menu()


@admin_required
@require_POST
def menu_item_save(request):
    """Band yoki ichki band qo'shish (`key` bo'sh) yoki tahrirlash."""
    from .menu import active_sections, save_item

    key = request.POST.get("key", "").strip()
    item, error = save_item(
        request.POST, active_sections(), key=key or None,
        group_code=request.POST.get("group", ""), parent_key=request.POST.get("parent", "") or None,
    )
    if error:
        messages.error(request, error)
        return _back_to_menu(f"g-{request.POST.get('group', '')}")
    log_action(request, "menu.item.edit" if key else "menu.item.add", item.key,
               label=item.label, page=item.page, url=item.url)
    messages.success(request, "Band saqlandi." if key else "Band qo‘shildi.")
    return _back_to_menu(f"g-{item.group.key}")


@admin_required
@require_POST
def menu_item_delete(request, key):
    from .menu import delete_item

    if not delete_item(key):
        messages.error(request, "Bu bandni o‘chirib bo‘lmaydi.")
    else:
        log_action(request, "menu.item.delete", key)
        messages.success(request, "Band o‘chirildi.")
    return _back_to_menu(request.POST.get("anchor", ""))


@admin_required
def menu_reset(request, group):
    """`groups` — bloklar tartibi; `all` — butun o'qituvchi menyusi; aks holda — bitta standart blok."""
    from django.http import Http404

    from .menu import DEFAULT_GROUPS, reset_all, reset_group, reset_group_order

    if group not in {"groups", "all"} and group not in DEFAULT_GROUPS:
        raise Http404
    if request.method == "POST":
        if group == "groups":
            reset_group_order()
            messages.success(request, "Bloklar standart tartibga qaytarildi.")
        elif group == "all":
            reset_all()
            messages.success(request, "O‘qituvchi menyusi to‘liq standart holatga qaytarildi.")
        else:
            reset_group(group)
            messages.success(request, f"«{DEFAULT_GROUPS[group]['title']}» standart holatga qaytarildi.")
        log_action(request, "menu.reset", group)
    return _back_to_menu()
