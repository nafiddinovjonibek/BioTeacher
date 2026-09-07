"""Maqsad qo'yish moduli view'lari (FR-13..FR-17)."""

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.forms import INPUT_CLASS, StyledFormMixin, TEXTAREA_CLASS
from accounts.permissions import require_student_access
from accounts.services import log_action

from .models import Goal, GoalTask


class GoalForm(StyledFormMixin, forms.ModelForm):
    """FR-13 — SMART shablon."""

    class Meta:
        model = Goal
        fields = ["title", "component", "why", "resources", "expected_result",
                  "start_date", "deadline"]
        labels = {
            "title": "Maqsad (aniq va o'lchanadigan)",
            "component": "Qaysi komponentni rivojlantiradi?",
            "why": "Nima uchun bu maqsad muhim?",
            "resources": "Resurslar (kitob, kurs, mentor, vaqt)",
            "expected_result": "Kutilayotgan natija — buni qanday tekshiraman?",
            "start_date": "Boshlanish sanasi",
            "deadline": "Muddat",
        }
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
            "deadline": forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
            "why": forms.Textarea(attrs={"rows": 3, "class": TEXTAREA_CLASS}),
            "resources": forms.Textarea(attrs={"rows": 3, "class": TEXTAREA_CLASS}),
            "expected_result": forms.Textarea(attrs={"rows": 3, "class": TEXTAREA_CLASS}),
        }

    def clean(self):
        cleaned = super().clean()
        start, deadline = cleaned.get("start_date"), cleaned.get("deadline")
        if start and deadline and deadline < start:
            self.add_error("deadline", "Muddat boshlanish sanasidan oldin bo'lishi mumkin emas.")
        return cleaned


TaskFormSet = inlineformset_factory(
    Goal,
    GoalTask,
    fields=["title", "week"],
    labels={"title": "Vazifa", "week": "Hafta"},
    extra=4,
    can_delete=True,
    widgets={
        "title": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Masalan: Muammoli ta'lim metodini o'rganish"}),
        "week": forms.NumberInput(attrs={"class": INPUT_CLASS, "min": 1, "max": 52}),
    },
)


@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user).prefetch_related("tasks")
    return render(
        request,
        "goals/list.html",
        {
            "active": [g for g in goals if g.is_active],
            "closed": [g for g in goals if not g.is_active],
        },
    )


@login_required
def goal_create(request):
    form = GoalForm(request.POST or None, initial={"deadline": timezone.localdate() + timezone.timedelta(days=28)})
    formset = TaskFormSet(request.POST or None, instance=Goal())
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        goal = form.save(commit=False)
        goal.user = request.user
        goal.save()
        formset.instance = goal
        formset.save()

        from progress.models import ActivityLog
        from progress.services import log_activity

        log_activity(request.user, ActivityLog.Action.GOAL_CREATED, object_ref=goal.title)
        log_action(request, "goal.create", goal.title)
        messages.success(request, "Maqsad belgilandi. Endi haftalik vazifalarni bajaring.")
        return redirect("goals:detail", pk=goal.pk)
    return render(request, "goals/form.html", {"form": form, "formset": formset, "is_new": True})


@login_required
def goal_detail(request, pk):
    goal = get_object_or_404(Goal.objects.prefetch_related("tasks"), pk=pk)
    require_student_access(request.user, goal.user)
    return render(
        request,
        "goals/detail.html",
        {"goal": goal, "can_edit": goal.user_id == request.user.pk},
    )


@login_required
def goal_edit(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    form = GoalForm(request.POST or None, instance=goal)
    formset = TaskFormSet(request.POST or None, instance=goal)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        messages.success(request, "Maqsad yangilandi.")
        return redirect("goals:detail", pk=goal.pk)
    return render(request, "goals/form.html", {"form": form, "formset": formset, "goal": goal})


@login_required
def toggle_task(request, pk):
    """FR-14 — vazifa checklisti (HTMX)."""
    task = get_object_or_404(GoalTask.objects.select_related("goal"), pk=pk)
    if task.goal.user_id != request.user.pk:
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied("Bu vazifa sizga tegishli emas.")
    task.toggle()

    if task.is_done:
        from progress.models import ActivityLog
        from progress.services import log_activity

        log_activity(request.user, ActivityLog.Action.GOAL_TASK, object_ref=task.title)
    return render(request, "goals/_tasks.html", {"goal": task.goal})


@login_required
def goal_close(request, pk):
    """FR-16 — yopishdan oldin yakuniy refleksiya majburiy."""
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if not goal.can_close():
        messages.warning(
            request,
            "Maqsadni yopishdan oldin yakuniy refleksiya yozing — bu FR-16 talabi.",
        )
        return redirect("goals:reflect", pk=goal.pk)

    goal.status = Goal.Status.DONE
    goal.completed_at = timezone.now()
    goal.save(update_fields=["status", "completed_at", "updated_at"])

    from gamification.services import evaluate_badges

    evaluate_badges(request.user)
    log_action(request, "goal.close", goal.title)
    messages.success(request, "Maqsad yakunlandi. Tabriklaymiz!")
    return redirect("goals:detail", pk=goal.pk)


@login_required
def goal_review(request, pk):
    """FR-17 — mentor maqsadga izoh qoldiradi va tasdiqlaydi."""
    goal = get_object_or_404(Goal.objects.select_related("user__profile__group"), pk=pk)
    profile = getattr(request.user, "profile", None)
    is_mentor = request.user.is_superuser or (
        profile and profile.is_teacher
        and getattr(goal.user.profile, "group", None)
        and goal.user.profile.group.teacher_id == request.user.pk
    )
    if not is_mentor:
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied("Bu maqsadga izoh qoldirish huquqingiz yo'q.")

    if request.method == "POST":
        goal.mentor_comment = request.POST.get("comment", "")[:2000]
        if request.POST.get("approve") == "1" and not goal.mentor_approved:
            goal.mentor_approved = True
            goal.mentor_approved_at = timezone.now()
        elif request.POST.get("approve") == "0":
            goal.mentor_approved = False
            goal.mentor_approved_at = None
        goal.save(update_fields=["mentor_comment", "mentor_approved",
                                 "mentor_approved_at", "updated_at"])

        from notifications.models import NotificationType
        from notifications.services import notify

        notify(
            goal.user,
            NotificationType.MENTOR_COMMENT,
            title=f"Maqsadingizga mentor izohi: {goal.title}",
            body=goal.mentor_comment or ("Maqsadingiz tasdiqlandi."
                                         if goal.mentor_approved else ""),
            url=f"/maqsadlar/{goal.pk}/",
        )
        log_action(request, "goal.review", goal.title, approved=goal.mentor_approved)
        messages.success(request, "Izoh saqlandi va talabaga xabar yuborildi.")
        return redirect("goals:detail", pk=goal.pk)

    return render(request, "goals/review.html", {"goal": goal})


@login_required
def goal_reflect(request, pk):
    """Maqsad yakuni bo'yicha refleksiya (FR-16)."""
    from reflection.services import save_with_score
    from reflection.views import TaskReflectionForm

    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    form = TaskReflectionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.user = request.user
        entry.kind = entry.Kind.GOAL
        entry.goal = goal
        entry.save()
        save_with_score(entry)
        messages.success(request, "Yakuniy refleksiya saqlandi. Endi maqsadni yopishingiz mumkin.")
        return redirect("goals:close", pk=goal.pk)
    return render(request, "goals/reflect.html", {"goal": goal, "form": form})
