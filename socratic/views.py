"""AI-sokratik suhbat sahifasi. Suhbat holati sessiyada saqlanadi."""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from accounts.services import log_action

from . import engine
from .scenarios import TOPICS

SESSION_KEY = "socratic"


def _state(request):
    state = request.session.get(SESSION_KEY)
    if not state or "turns" not in state:
        state, _ = engine.start(None)
        request.session[SESSION_KEY] = state
    return state


def _save(request, state):
    request.session[SESSION_KEY] = state
    request.session.modified = True


def _payload(request):
    """JSON (fetch) yoki oddiy forma — ikkalasini ham qabul qiladi."""
    if request.content_type == "application/json":
        try:
            return json.loads(request.body or "{}"), True
        except json.JSONDecodeError:
            return {}, True
    return request.POST, False


def _response(state, is_json, reply=""):
    if is_json:
        return JsonResponse({"reply": reply, "progress": engine.progress(state),
                             "can_save": state["phase"] == "done"})
    return redirect("socratic:chat")


@login_required
def chat(request):
    state = _state(request)
    return render(
        request,
        "socratic/chat.html",
        {
            "turns": state["turns"],
            "progress": engine.progress(state),
            "can_save": state["phase"] == "done",
            "topics": [{"key": key, **{k: t[k] for k in ("title", "icon", "section", "teaser")}}
                       for key, t in TOPICS.items()],
        },
    )


@login_required
@require_POST
def start(request):
    data, is_json = _payload(request)
    state, text = engine.start(data.get("topic"))
    _save(request, state)
    return _response(state, is_json, text)


@login_required
@require_POST
def message(request):
    data, is_json = _payload(request)
    state = _state(request)
    text = engine.reply(state, data.get("message", ""))
    _save(request, state)
    return _response(state, is_json, text)


@login_required
@require_POST
def save(request):
    """Yakunlangan suhbat xulosasi refleksiya kundaligiga (erkin yozuv)."""
    from reflection.models import ReflectionEntry
    from reflection.services import save_with_score

    state = _state(request)
    if state["phase"] != "done":
        messages.error(request, "Avval suhbatni xulosa bilan yakunlang.")
        return redirect("socratic:chat")

    entry = ReflectionEntry.objects.create(
        user=request.user,
        kind=ReflectionEntry.Kind.FREE,
        q1=state.get("conclusion", ""),
        free_text=f"AI-sokratik suhbati: {engine.title(state)}\n\n{engine.transcript(state)}",
        tags=",".join(filter(None, ["ai-sokratik", state["topic"]])),
    )
    save_with_score(entry)
    log_action(request, "socratic.save", state["topic"] or "erkin")
    state, _ = engine.start(None)
    _save(request, state)
    messages.success(request, "Suhbat xulosasi refleksiya kundaligiga saqlandi.")
    return redirect("reflection:detail", pk=entry.pk)
