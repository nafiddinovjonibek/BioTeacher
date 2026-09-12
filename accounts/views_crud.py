"""
Admin uchun universal CRUD view'lari (`accounts.crud` reyestri asosida).

Barcha sahifalar faqat ADMIN roliga ochiq. Har bir harakat audit jurnaliga yoziladi.
"""

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import modelform_factory
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .crud import get_config, grouped
from .forms_manage import BaseManageForm, manage_formfield
from .permissions import admin_required
from .services import log_action

PER_PAGE = 30
SKIP_FIELDS = {"id", "created_at", "updated_at", "is_deleted", "deleted_at"}


def _config_or_404(key):
    config = get_config(key)
    if config is None:
        raise Http404("Bunday bo'lim yo'q.")
    return config


def _editable_fields(model):
    return [
        f.name for f in model._meta.fields
        if f.editable and not f.auto_created and f.name not in SKIP_FIELDS
    ]


def _form_class(config):
    if config.form_class:
        return config.form_class
    fields = config.fields or _editable_fields(config.model)
    form_cls = modelform_factory(
        config.model, form=BaseManageForm, fields=fields, formfield_callback=manage_formfield
    )
    form_cls.slug_from = config.slug_from
    return form_cls


def _active_filters(request, config):
    """GET'dagi ruxsat etilgan filtrlar: {"section": "3", ...}."""
    return {name: request.GET[name] for name in config.filters if request.GET.get(name)}


def _list_url(config, filters=None):
    url = reverse("manage:crud_list", args=[config.key])
    if filters:
        from urllib.parse import urlencode
        url += "?" + urlencode(filters)
    return url


def _object_or_404(config, pk, deleted=False):
    return get_object_or_404(config.base_queryset(deleted=deleted), pk=pk)


# ------------------------------------------------------------------ hub

@admin_required
def crud_index(request):
    groups = []
    for code, name, icon, items in grouped():
        rows = [{"config": c, "count": c.base_queryset().count()} for c in items]
        groups.append({"code": code, "name": name, "icon": icon, "rows": rows})
    from .builders import builder_kinds

    return render(request, "manage/index.html", {"groups": groups, "builders": builder_kinds()})


# ----------------------------------------------------------------- list

@admin_required
def crud_list(request, key):
    config = _config_or_404(key)
    show_deleted = config.soft_delete and request.GET.get("deleted") == "1"
    queryset = config.base_queryset(deleted=show_deleted)

    filters = _active_filters(request, config)
    if filters:
        queryset = queryset.filter(**filters)

    query = request.GET.get("q", "").strip()
    if query and config.search:
        cond = Q()
        for lookup in config.search:
            cond |= Q(**{f"{lookup}__icontains": query})
        queryset = queryset.filter(cond)

    paginator = Paginator(queryset, PER_PAGE)
    page = paginator.get_page(request.GET.get("page"))

    # Filtr yorlig'i: FK bo'lsa obyekt nomi, aks holda qiymat.
    filter_labels = []
    for name, value in filters.items():
        label = value
        try:
            db_field = config.model._meta.get_field(name.split("__")[0])
            if db_field.is_relation and "__" not in name:
                obj = db_field.related_model._default_manager.filter(pk=value).first()
                label = str(obj) if obj else value
            elif db_field.choices:
                label = dict(db_field.flatchoices).get(value, value)
        except Exception:
            pass
        filter_labels.append((name, label))

    return render(
        request,
        "manage/crud_list.html",
        {
            "config": config,
            "page": page,
            "query": query,
            "filters": filters,
            "filter_labels": filter_labels,
            "show_deleted": show_deleted,
            "deleted_count": (
                config.base_queryset(deleted=True).count() if config.soft_delete else 0
            ),
            "add_url": reverse("manage:crud_create", args=[config.key])
            + ("?" + request.GET.urlencode() if filters else ""),
        },
    )


# ------------------------------------------------------------ create/edit

def _render_form(request, config, form, obj=None):
    return render(
        request,
        "manage/crud_form.html",
        {"config": config, "form": form, "obj": obj, "is_new": obj is None,
         "back_url": _list_url(config, _active_filters(request, config)),
         "multipart": form.is_multipart()},
    )


@admin_required
def crud_create(request, key):
    config = _config_or_404(key)
    if not config.can_add:
        messages.error(request, "Bu bo'limda yangi yozuv yaratib bo'lmaydi.")
        return redirect("manage:crud_list", key=key)

    form_cls = _form_class(config)
    initial = {k: v for k, v in _active_filters(request, config).items() if "__" not in k}
    form = form_cls(request.POST or None, request.FILES or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        log_action(request, f"manage.{config.key}.create", str(obj)[:200])
        messages.success(request, f"{config.singular.capitalize()} yaratildi: {obj}")
        if request.POST.get("_continue"):
            return redirect("manage:crud_edit", key=key, pk=obj.pk)
        if request.POST.get("_addanother"):
            return redirect(request.get_full_path())
        return redirect(_list_url(config, _active_filters(request, config)))
    return _render_form(request, config, form)


@admin_required
def crud_edit(request, key, pk):
    config = _config_or_404(key)
    obj = _object_or_404(config, pk)
    if not config.can_edit:
        messages.error(request, "Bu yozuvni tahrirlab bo'lmaydi.")
        return redirect("manage:crud_list", key=key)

    form_cls = _form_class(config)
    form = form_cls(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        log_action(request, f"manage.{config.key}.update", str(obj)[:200])
        messages.success(request, f"{config.singular.capitalize()} saqlandi: {obj}")
        if request.POST.get("_continue"):
            return redirect("manage:crud_edit", key=key, pk=obj.pk)
        return redirect(_list_url(config, _active_filters(request, config)))
    return _render_form(request, config, form, obj)


# ----------------------------------------------------------------- delete

@admin_required
def crud_delete(request, key, pk):
    """Soft-delete modellar arxivga tushadi; qolganlari butunlay o'chadi; Measurement — void."""
    config = _config_or_404(key)
    obj = _object_or_404(config, pk)
    if not config.can_delete:
        messages.error(request, "Bu yozuvni o'chirib bo'lmaydi.")
        return redirect("manage:crud_list", key=key)
    if config.model is request.user.__class__ and obj.pk == request.user.pk:
        messages.error(request, "O'zingizni o'chira olmaysiz.")
        return redirect("manage:crud_list", key=key)

    if config.delete_mode == "void":
        action, title = "void", "Bekor qilish (void)"
    elif config.soft_delete:
        action, title = "archive", "Arxivga o'tkazish"
    else:
        action, title = "delete", "Butunlay o'chirish"

    if request.method == "POST":
        label = str(obj)[:200]
        if action == "void":
            obj.void(request.POST.get("reason", "admin"))
        elif action == "archive":
            obj.delete()
        else:
            obj.delete()
        log_action(request, f"manage.{config.key}.{action}", label)
        messages.success(request, f"{config.singular.capitalize()} — {title.lower()} bajarildi.")
        return redirect(_list_url(config, _active_filters(request, config)))

    return render(
        request,
        "manage/crud_confirm.html",
        {"config": config, "obj": obj, "action": action, "title": title,
         "back_url": _list_url(config, _active_filters(request, config))},
    )


@admin_required
def crud_restore(request, key, pk):
    config = _config_or_404(key)
    if not config.soft_delete:
        raise Http404
    obj = _object_or_404(config, pk, deleted=True)
    if request.method == "POST":
        obj.restore()
        log_action(request, f"manage.{config.key}.restore", str(obj)[:200])
        messages.success(request, f"{config.singular.capitalize()} tiklandi: {obj}")
    return redirect(_list_url(config, {"deleted": "1"}))


@admin_required
def crud_purge(request, key, pk):
    """Arxivdagi yozuvni bazadan butunlay o'chirish."""
    config = _config_or_404(key)
    if not config.soft_delete:
        raise Http404
    obj = _object_or_404(config, pk, deleted=True)
    if request.method == "POST":
        label = str(obj)[:200]
        obj.hard_delete()
        log_action(request, f"manage.{config.key}.purge", label)
        messages.success(request, f"{config.singular.capitalize()} butunlay o'chirildi.")
        return redirect(_list_url(config, {"deleted": "1"}))
    return render(
        request,
        "manage/crud_confirm.html",
        {"config": config, "obj": obj, "action": "purge", "title": "Butunlay o'chirish",
         "back_url": _list_url(config, {"deleted": "1"})},
    )


# ---------------------------------------------------------------- reorder

@admin_required
@require_POST
def crud_reorder(request, key):
    """Drag & drop: {"ids": [..]} — ro'yxatdagi tartib bo'yicha `order` yangilanadi."""
    import json

    config = _config_or_404(key)
    if not config.orderable:
        raise Http404
    try:
        ids = [int(i) for i in json.loads(request.body or "{}").get("ids", [])]
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "noto'g'ri ma'lumot"}, status=400)
    objects = {o.pk: o for o in config.base_queryset().filter(pk__in=ids)}
    for position, pk in enumerate(ids):
        obj = objects.get(pk)
        if obj is not None and obj.order != position:
            obj.order = position
            obj.save(update_fields=["order"])
    log_action(request, f"manage.{config.key}.reorder", f"{len(ids)} ta")
    return JsonResponse({"ok": True, "count": len(ids)})
