from django.contrib import admin

from .models import Lesson, LessonProgress, Material, Section, Topic


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 0
    prepopulated_fields = {"slug": ("title",)}
    show_change_link = True


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("title", "slug", "duration_minutes", "pass_threshold", "quiz", "order", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    show_change_link = True


class MaterialInline(admin.TabularInline):
    model = Material
    extra = 0


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [TopicInline]


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "component", "order", "is_active")
    list_filter = ("section", "component", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "duration_minutes", "pass_threshold", "is_active")
    list_filter = ("topic__section", "is_active")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [MaterialInline]


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "status", "score", "attempts", "completed_at")
    list_filter = ("status",)
    search_fields = ("user__email",)
