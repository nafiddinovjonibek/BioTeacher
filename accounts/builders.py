"""
Sodda "quruvchi" sahifalar — bog'liq yozuvlarni BITTA sahifada yaratish/tahrirlash.

• `test`   — so'rovnoma + savollar + variantlar (JSON orqali, JS bilan).
• qolganlari — ota-yozuv + bola-yozuvlar inline formset bilan:
  rubrika+mezonlar, nishon+qoidalar, dars+materiallar, fan+mavzular, mavzu+darslar.
"""

import json

from django.contrib import messages
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from core.enums import BloomLevel, Component

from .crud import get_config
from .forms_manage import BaseManageForm, _has_field, manage_formfield
from .permissions import admin_required
from .services import log_action
from .views_crud import _form_class

# ------------------------------------------------------------------ inline

INLINE_BUILDERS = {
    "rubrika": {
        "parent_key": "rubrics", "child": ("assignments", "Criterion"), "fk": "rubric",
        "fields": ["name", "hint", "weight", "max_score"],
        "child_title": "Mezonlar", "hint": "Har bir mezon uchun maksimal ball va vazn. Umumiy foiz avtomatik hisoblanadi.",
    },
    "nishon": {
        "parent_key": "badges", "child": ("gamification", "BadgeRule"), "fk": "badge",
        "fields": ["metric", "threshold", "is_active"],
        "child_title": "Berish qoidalari", "hint": "Metrika chegaraga yetganda nishon avtomatik beriladi.",
    },
    "dars": {
        "parent_key": "lessons", "child": ("content", "Material"), "fk": "lesson",
        "fields": ["kind", "title", "body", "url", "file"],
        "child_title": "Materiallar", "hint": "Matn, rasm, video, PDF yoki havola.",
    },
    "fan": {
        "parent_key": "sections", "child": ("content", "Topic"), "fk": "section",
        "fields": ["title", "component", "summary", "is_active"],
        "child_title": "Mavzular", "hint": "Mavzu slugi sarlavhadan avtomatik yasaladi.",
        "child_slug_from": "title",
    },
    "mavzu": {
        "parent_key": "topics", "child": ("content", "Lesson"), "fk": "topic",
        "fields": ["title", "duration_minutes", "pass_threshold", "quiz", "is_active"],
        "child_title": "Darslar", "hint": "Dars matni va materiallarini keyin \"Dars\" quruvchisida to'ldirasiz.",
        "child_slug_from": "title",
    },
}

BUILDER_TITLES = {
    "test": "Test / anketa",
    "rubrika": "Rubrika",
    "nishon": "Nishon",
    "dars": "Dars",
    "fan": "Fan",
    "mavzu": "Mavzu",
}


def builder_kinds():
    """Hub sahifasidagi "Tez yaratish" tugmalari."""
    return [(kind, title) for kind, title in BUILDER_TITLES.items()]


def _child_model(spec):
    from django.apps import apps

    return apps.get_model(*spec["child"])


@admin_required
def builder(request, kind, pk=None):
    if kind == "test":
        return quiz_builder(request, pk)
    spec = INLINE_BUILDERS.get(kind)
    if spec is None:
        raise Http404("Bunday quruvchi yo'q.")
    return inline_builder(request, kind, spec, pk)


def inline_builder(request, kind, spec, pk):
    config = get_config(spec["parent_key"])
    parent_model = config.model
    child_model = _child_model(spec)
    obj = get_object_or_404(config.base_queryset(), pk=pk) if pk else None

    parent_form_cls = _form_class(config)
    formset_cls = inlineformset_factory(
        parent_model, child_model, form=BaseManageForm, fields=spec["fields"],
        formfield_callback=manage_formfield, extra=0 if obj else 1,
        can_delete=True, can_order=True,  # ORDER — drag & drop tartib uchun
    )
    form = parent_form_cls(request.POST or None, request.FILES or None, instance=obj)
    formset = formset_cls(request.POST or None, request.FILES or None, instance=obj)

    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            parent = form.save()
            formset.instance = parent
            has_order = _has_field(child_model, "order")
            # ordered_forms — o'chirilmaganlar, sahifadagi (drag qilingan) tartibda.
            for position, child_form in enumerate(formset.ordered_forms):
                setattr(child_form.instance, spec["fk"], parent)
                if has_order:
                    child_form.instance.order = position
                child_form.save()
            for child_form in formset.deleted_forms:
                if child_form.instance.pk:
                    child_form.instance.delete()
        log_action(request, f"manage.{kind}.{'update' if obj else 'create'}", str(parent)[:200])
        messages.success(request, f"{BUILDER_TITLES[kind]} saqlandi: {parent}")
        if request.POST.get("_continue"):
            return redirect("manage:builder_edit", kind=kind, pk=parent.pk)
        return redirect("manage:crud_list", key=config.key)

    return render(
        request,
        "manage/inline_builder.html",
        {
            "kind": kind, "title": BUILDER_TITLES[kind], "config": config, "obj": obj,
            "form": form, "formset": formset, "child_title": spec["child_title"],
            "hint": spec.get("hint", ""),
            "multipart": form.is_multipart() or formset.is_multipart(),
            "back_url": reverse("manage:crud_list", args=[config.key]),
        },
    )


# ------------------------------------------------------------------- quiz

# Quruvchida Bloom darajalari tushunarli izoh bilan ko'rsatiladi.
BLOOM_LABELS = [
    (BloomLevel.KNOW.value, "1 — Bilish: faktni eslab qolish, aytib berish"),
    (BloomLevel.UNDERSTAND.value, "2 — Tushunish: o'z so'zi bilan izohlash, misol keltirish"),
    (BloomLevel.APPLY.value, "3 — Qo'llash: bilimni yangi vaziyatda ishlatish"),
    (BloomLevel.ANALYZE.value, "4 — Tahlil: qismlarga ajratish, sabab-oqibat"),
    (BloomLevel.EVALUATE.value, "5 — Baholash: asoslab xulosa chiqarish"),
    (BloomLevel.CREATE.value, "6 — Yaratish: yangi yechim/loyiha ishlab chiqish"),
]

QUIZ_FIELDS = ["title", "slug", "kind", "cut", "description", "instruction",
               "question_count", "time_limit_minutes", "shuffle_questions", "is_active"]


def _serialize_questions(questionnaire):
    if questionnaire is None:
        return []
    rows = []
    for q in questionnaire.questions.order_by("order", "id").prefetch_related("choices"):
        rows.append({
            "id": q.pk, "text": q.text, "component": q.component, "bloom_level": q.bloom_level,
            "reverse_scored": q.reverse_scored, "explanation": q.explanation,
            "choices": [{"id": c.pk, "text": c.text, "is_correct": c.is_correct}
                        for c in q.choices.all()],
        })
    return rows


def _validate_questions(items, kind):
    from diagnostics.models import Questionnaire

    errors = []
    if not isinstance(items, list):
        return ["Savollar ro'yxati noto'g'ri formatda."]
    if not items:
        errors.append("Kamida bitta savol qo'shing.")
    needs_choices = kind != Questionnaire.Kind.LIKERT
    for i, item in enumerate(items, start=1):
        if not str(item.get("text", "")).strip():
            errors.append(f"{i}-savol matni bo'sh.")
        if item.get("component") not in Component.values:
            errors.append(f"{i}-savol: komponent tanlanmagan.")
        if needs_choices:
            choices = [c for c in item.get("choices", []) if str(c.get("text", "")).strip()]
            if len(choices) < 2:
                errors.append(f"{i}-savol: kamida 2 ta variant kerak.")
            elif sum(1 for c in choices if c.get("is_correct")) != 1:
                errors.append(f"{i}-savol: aynan bitta to'g'ri variant belgilang.")
    return errors


def _sync_questions(questionnaire, items):
    from diagnostics.models import Choice, Question, Questionnaire

    needs_choices = questionnaire.kind != Questionnaire.Kind.LIKERT
    keep = []
    for order, item in enumerate(items):
        question = None
        if item.get("id"):
            question = Question.all_objects.filter(pk=item["id"], questionnaire=questionnaire).first()
        if question is None:
            question = Question(questionnaire=questionnaire)
        question.text = str(item.get("text", "")).strip()
        question.component = item.get("component")
        try:
            question.bloom_level = int(item.get("bloom_level") or BloomLevel.KNOW)
        except (TypeError, ValueError):
            question.bloom_level = BloomLevel.KNOW
        question.reverse_scored = bool(item.get("reverse_scored")) and not needs_choices
        question.explanation = str(item.get("explanation", "")).strip()
        question.order = order
        question.is_active = True
        question.is_deleted = False
        question.deleted_at = None
        question.save()
        keep.append(question.pk)

        if needs_choices:
            keep_choices = []
            for c_order, choice_item in enumerate(item.get("choices", [])):
                text = str(choice_item.get("text", "")).strip()
                if not text:
                    continue
                choice = None
                if choice_item.get("id"):
                    choice = Choice.objects.filter(pk=choice_item["id"], question=question).first()
                if choice is None:
                    choice = Choice(question=question)
                choice.text = text[:500]
                choice.is_correct = bool(choice_item.get("is_correct"))
                choice.order = c_order
                choice.save()
                keep_choices.append(choice.pk)
            question.choices.exclude(pk__in=keep_choices).delete()
        else:
            question.choices.all().delete()

    for stale in Question.objects.filter(questionnaire=questionnaire).exclude(pk__in=keep):
        stale.delete()  # soft — eski javoblar buzilmaydi


def _quiz_config(kind=None):
    """
    Quruvchi bitta, ro'yxat esa ikkita: variantli testlar va Likert anketalar.

    Yozuvning turiga qarab mos bo'limni qaytaradi — "Orqaga" havolasi va
    saqlagandan keyingi redirect shu bo'limga olib boradi.
    """
    from diagnostics.models import Questionnaire

    return get_config("questionnaires" if kind == Questionnaire.Kind.LIKERT else "tests")


def quiz_builder(request, pk=None):
    from diagnostics.models import Questionnaire

    # Turi (test/anketa) obyektdan, yangi yozuvda esa formadan yoki havoladan olinadi.
    obj = get_object_or_404(Questionnaire.objects.all(), pk=pk) if pk else None
    kind_hint = obj.kind if obj else (request.POST.get("kind") or request.GET.get("kind") or "")
    if kind_hint not in Questionnaire.Kind.values:
        kind_hint = ""
    config = _quiz_config(kind_hint or None)
    form_cls = _form_class(config)
    form = form_cls(request.POST or None, instance=obj,
                    initial={"kind": kind_hint} if kind_hint and obj is None else None)
    question_errors = []
    posted_questions = None

    if request.method == "POST":
        try:
            posted_questions = json.loads(request.POST.get("questions_json") or "[]")
        except json.JSONDecodeError:
            posted_questions = []
            question_errors.append("Savollar ma'lumoti o'qilmadi — sahifani yangilab qayta urinib ko'ring.")
        if form.is_valid():
            question_errors += _validate_questions(posted_questions, form.cleaned_data["kind"])
            if not question_errors:
                with transaction.atomic():
                    questionnaire = form.save()
                    _sync_questions(questionnaire, posted_questions)
                log_action(request, f"manage.test.{'update' if obj else 'create'}", questionnaire.title)
                saved_config = _quiz_config(questionnaire.kind)
                messages.success(
                    request,
                    f"{saved_config.singular.capitalize()} saqlandi: {questionnaire.title} "
                    f"({len(posted_questions)} ta savol)."
                )
                if request.POST.get("_continue"):
                    return redirect("manage:builder_edit", kind="test", pk=questionnaire.pk)
                return redirect("manage:crud_list", key=saved_config.key)

    initial_questions = posted_questions if posted_questions is not None else _serialize_questions(obj)
    return render(
        request,
        "manage/quiz_builder.html",
        {
            "form": form, "obj": obj, "config": config,
            "questions_json": initial_questions,
            "question_errors": question_errors,
            "components": [(c.value, f"{c.value} — {c.label}") for c in Component],
            "bloom_levels": BLOOM_LABELS,
            "likert_kind": Questionnaire.Kind.LIKERT,
            "back_url": reverse("manage:crud_list", args=[config.key]),
        },
    )
