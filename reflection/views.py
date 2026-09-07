"""Refleksiya kundaligi view'lari (FR-38..FR-42)."""

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import StyledFormMixin, TEXTAREA_CLASS
from accounts.permissions import require_student_access
from accounts.services import log_action
from assignments.models import Submission

from .models import MIN_ANSWER_LENGTH, ReflectionEntry, ReflectionPrompt
from .services import save_with_score


class TaskReflectionForm(StyledFormMixin, forms.ModelForm):
    """FR-38, FR-40 — 4 majburiy savol, minimal hajm nazorati."""

    class Meta:
        model = ReflectionEntry
        fields = ["q1", "q2", "q3", "q4", "tags"]
        widgets = {
            "q1": forms.Textarea(attrs={"rows": 3}),
            "q2": forms.Textarea(attrs={"rows": 3}),
            "q3": forms.Textarea(attrs={"rows": 3}),
            "q4": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        prompts = {p.slot: p for p in ReflectionPrompt.objects.filter(is_active=True)}
        for index, field in enumerate(["q1", "q2", "q3", "q4"], start=1):
            prompt = prompts.get(index)
            if prompt:
                self.fields[field].label = prompt.text
                self.fields[field].help_text = prompt.hint
            self.fields[field].required = True

    def clean(self):
        cleaned = super().clean()
        total = sum(len((cleaned.get(f) or "").strip()) for f in ["q1", "q2", "q3", "q4"])
        if total < MIN_ANSWER_LENGTH:
            raise forms.ValidationError(
                f"Refleksiya juda qisqa ({total} belgi). Kamida {MIN_ANSWER_LENGTH} belgi yozing — "
                "bu shablon javoblarning oldini oladi va REF ko'rsatkichingizga ta'sir qiladi."
            )
        return cleaned


class FreeReflectionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ReflectionEntry
        fields = ["free_text", "tags"]
        labels = {"free_text": "Bugungi yozuv", "tags": "Teglar (vergul bilan)"}
        widgets = {"free_text": forms.Textarea(attrs={"rows": 8, "class": TEXTAREA_CLASS})}

    def clean_free_text(self):
        text = self.cleaned_data["free_text"].strip()
        if len(text) < MIN_ANSWER_LENGTH:
            raise forms.ValidationError(
                f"Kamida {MIN_ANSWER_LENGTH} belgi yozing (hozir {len(text)})."
            )
        return text


@login_required
def journal(request):
    """FR-39 — sana bo'yicha lenta, teg va qidiruv."""
    entries = ReflectionEntry.objects.filter(user=request.user)
    query = request.GET.get("q", "").strip()
    tag = request.GET.get("tag", "").strip()
    if query:
        entries = entries.filter(
            Q(q1__icontains=query) | Q(q2__icontains=query) | Q(q3__icontains=query)
            | Q(q4__icontains=query) | Q(free_text__icontains=query)
        )
    if tag:
        entries = entries.filter(tags__icontains=tag)

    all_tags = set()
    for row in ReflectionEntry.objects.filter(user=request.user).values_list("tags", flat=True):
        all_tags.update(t.strip() for t in (row or "").split(",") if t.strip())

    return render(
        request,
        "reflection/journal.html",
        {"entries": entries[:100], "query": query, "tag": tag, "tags": sorted(all_tags)},
    )


@login_required
def create_free(request):
    form = FreeReflectionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.user = request.user
        entry.kind = ReflectionEntry.Kind.FREE
        entry.save()
        save_with_score(entry)
        log_action(request, "reflection.create", "free")
        messages.success(request, "Yozuv saqlandi.")
        return redirect("reflection:journal")
    return render(request, "reflection/create_free.html", {"form": form})


@login_required
def create_for_submission(request, submission_id):
    """FR-38 — topshiriq yakunidagi majburiy refleksiya."""
    submission = get_object_or_404(Submission, pk=submission_id, student=request.user)
    existing = submission.reflections.first()
    if existing:
        return redirect("reflection:detail", pk=existing.pk)

    form = TaskReflectionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.user = request.user
        entry.kind = ReflectionEntry.Kind.TASK
        entry.submission = submission
        entry.save()
        save_with_score(entry)
        log_action(request, "reflection.create", f"submission:{submission.pk}")
        messages.success(
            request,
            f"Refleksiya saqlandi. Sifat bahosi: {entry.quality_score:.0f} %.",
        )
        return redirect("reflection:detail", pk=entry.pk)

    return render(
        request,
        "reflection/create_task.html",
        {"form": form, "submission": submission, "min_length": MIN_ANSWER_LENGTH},
    )


@login_required
def detail(request, pk):
    entry = get_object_or_404(ReflectionEntry.objects.select_related("user"), pk=pk)
    require_student_access(request.user, entry.user)  # FR-42 — faqat talaba va mentori
    return render(request, "reflection/detail.html", {"entry": entry})
