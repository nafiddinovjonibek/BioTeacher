"""BioBilim moduli view'lari (FR-18..FR-21)."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.services import log_action
from diagnostics.services import compute_attempt_scores, get_or_start_attempt, save_answer

from .models import Lesson, LessonProgress, Section, Topic


# Mavzu kartasidagi rasm — mavzu slugiga qarab. Yangi mavzu qo'shilsa,
# rasmni static/img/ ga qo'yib, shu yerga bitta qator qo'shiladi.
# Rasmsiz mavzu ikonka bilan ko'rsatiladi.
TOPIC_IMAGES = {
    "hujayra-tuzilishi": "img/topic-cell.jpg",
    "fotosintez": "img/topic-photo.jpg",
    "irsiyat-asoslari": "img/topic-dna.jpg",
    "ekotizim": "img/topic-ecosystem.jpg",
    "faol-talim-metodlari": "img/topic-teaching.jpg",
}

# Mavzu kartasidagi ikonka — bo'lim slugiga qarab tanlanadi.
TOPIC_ICONS = {
    "hujayra-biologiyasi": "microscope",
    "genetika": "dna",
    "ekologiya": "globe",
    "metodika": "users",
}


@login_required
def index(request):
    """FR-18 — bo'limlar va mavzular ierarxiyasi + o'zlashtirish holati."""
    progress = {p.lesson_id: p for p in LessonProgress.objects.filter(user=request.user)}
    passed_ids = {
        lesson_id for lesson_id, row in progress.items()
        if row.status == LessonProgress.Status.PASSED
    }

    sections = []
    for section in Section.objects.filter(is_active=True).prefetch_related("topics__lessons"):
        icon = TOPIC_ICONS.get(section.slug, "leaf")
        topics = []
        for topic in section.topics.filter(is_active=True):
            lessons = list(topic.lessons.filter(is_active=True))
            done = sum(1 for lesson in lessons if lesson.id in passed_ids)
            topics.append({
                "topic": topic, "lessons": lessons, "icon": icon,
                "image": TOPIC_IMAGES.get(topic.slug),
                "done": done, "total": len(lessons),
                "percent": round(done / len(lessons) * 100) if lessons else 0,
                "passed_ids": passed_ids,
            })
        if topics:
            sections.append({"section": section, "icon": icon, "topics": topics})

    total = Lesson.objects.filter(is_active=True).count()
    return render(
        request,
        "content/index.html",
        {
            "sections": sections,
            "passed": len(passed_ids),
            "total": total,
            "percent": round(len(passed_ids) / total * 100) if total else 0,
            "ring_offset": round(264 * (1 - (len(passed_ids) / total if total else 0)), 1),
        },
    )


@login_required
def section_detail(request, slug):
    """Bo'lim sahifasi — mavzular va ularning o'zlashtirish holati."""
    section = get_object_or_404(
        Section.objects.prefetch_related("topics__lessons"), slug=slug, is_active=True
    )
    progress = {p.lesson_id: p for p in LessonProgress.objects.filter(user=request.user)}
    topics = []
    for topic in section.topics.filter(is_active=True):
        lessons = list(topic.lessons.filter(is_active=True))
        done = sum(
            1 for lesson in lessons
            if progress.get(lesson.id) and progress[lesson.id].status == LessonProgress.Status.PASSED
        )
        topics.append({
            "topic": topic, "lessons": lessons, "done": done, "total": len(lessons),
            "percent": round(done / len(lessons) * 100) if lessons else 0,
        })
    return render(request, "content/section.html", {"section": section, "topics": topics})


@login_required
def topic_detail(request, section_slug, topic_slug):
    topic = get_object_or_404(
        Topic.objects.select_related("section").prefetch_related("lessons"),
        section__slug=section_slug,
        slug=topic_slug,
        is_active=True,
    )
    progress = {p.lesson_id: p for p in LessonProgress.objects.filter(user=request.user)}
    return render(request, "content/topic.html", {"topic": topic, "progress": progress})


@login_required
def lesson_detail(request, section_slug, topic_slug, lesson_slug):
    lesson = get_object_or_404(
        Lesson.objects.select_related("topic__section", "quiz").prefetch_related("materials"),
        topic__section__slug=section_slug,
        topic__slug=topic_slug,
        slug=lesson_slug,
        is_active=True,
    )
    progress, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    siblings = list(lesson.topic.lessons.filter(is_active=True))
    index = siblings.index(lesson) if lesson in siblings else 0
    return render(
        request,
        "content/lesson.html",
        {
            "lesson": lesson,
            "progress": progress,
            "prev": siblings[index - 1] if index > 0 else None,
            "next": siblings[index + 1] if index + 1 < len(siblings) else None,
        },
    )


@login_required
def lesson_quiz(request, pk):
    """FR-20 — darsning mustahkamlash testi."""
    lesson = get_object_or_404(Lesson.objects.select_related("quiz"), pk=pk, is_active=True)
    if lesson.quiz is None:
        messages.info(request, "Bu darsda test yo'q.")
        return redirect("content:index")

    attempt, _ = get_or_start_attempt(request.user, lesson.quiz)
    questions = attempt.questions()

    if request.method == "POST":
        from diagnostics.models import Choice, Question

        for question in questions:
            raw = request.POST.get(f"q{question.pk}")
            if not raw:
                continue
            choice = Choice.objects.filter(pk=raw, question=question).first()
            if choice:
                save_answer(attempt, question, choice=choice)

        scores = compute_attempt_scores(attempt)
        percent = round(sum(scores.values()) / len(scores), 1) if scores else 0.0
        attempt.scores = scores
        attempt.status = attempt.Status.FINISHED
        from django.utils import timezone

        attempt.finished_at = timezone.now()
        attempt.save(update_fields=["scores", "status", "finished_at", "updated_at"])

        progress, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        status = progress.mark(percent)

        from progress.models import ActivityLog
        from progress.services import log_activity, recompute

        log_activity(request.user, ActivityLog.Action.LESSON_DONE, object_ref=lesson.title)
        recompute(request.user)
        log_action(request, "lesson.quiz", lesson.slug)

        if status == LessonProgress.Status.PASSED:
            messages.success(request, f"Dars o'zlashtirildi — {percent:.0f} %.")
        else:
            messages.warning(
                request,
                f"Natija {percent:.0f} % — chegara {lesson.pass_threshold} %. "
                "Dars materialini qayta ko'rib chiqing (FR-21).",
            )
        return redirect(
            "content:lesson",
            section_slug=lesson.topic.section.slug,
            topic_slug=lesson.topic.slug,
            lesson_slug=lesson.slug,
        )

    return render(
        request, "content/quiz.html", {"lesson": lesson, "attempt": attempt, "questions": questions}
    )
