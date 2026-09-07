from django.contrib import admin

from .models import (
    Answer,
    Attempt,
    Choice,
    Measurement,
    Question,
    Questionnaire,
    Recommendation,
    ScoringWeights,
)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ("text", "component", "bloom_level", "reverse_scored", "order", "is_active")
    show_change_link = True


@admin.register(ScoringWeights)
class ScoringWeightsAdmin(admin.ModelAdmin):
    """SR-04 / SR-05 — vaznlarni bu yerdan sozlaysiz."""

    list_display = ("name", "mot", "cog", "act", "ref", "cre", "is_active")
    list_editable = ("mot", "cog", "act", "ref", "cre", "is_active")
    fieldsets = (
        (None, {"fields": ("name", "is_active")}),
        ("Vaznlar", {
            "fields": ("mot", "cog", "act", "ref", "cre"),
            "description": "Yig'indi avtomatik 1.00 ga normallashtiriladi. "
                           "O'zgartirish faqat KEYINGI o'lchovlarga ta'sir qiladi — "
                           "eski o'lchovlar o'z vaznlarini saqlab qoladi (SR-05).",
        }),
    )


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "cut", "question_count", "time_limit_minutes", "is_active")
    list_filter = ("kind", "cut", "is_active")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "questionnaire", "component", "bloom_level", "reverse_scored", "is_active")
    list_filter = ("questionnaire", "component", "bloom_level", "reverse_scored", "is_active")
    search_fields = ("text",)
    inlines = [ChoiceInline]

    @admin.display(description="savol")
    def short_text(self, obj):
        return obj.text[:80]


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "questionnaire", "cut", "status", "started_at", "finished_at")
    list_filter = ("status", "cut", "questionnaire")
    search_fields = ("user__email",)
    readonly_fields = ("scores", "question_order")


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    """TZ 6.3 — muzlatilgan: faqat o'qish va bekor qilish."""

    list_display = ("user", "cut", "mot", "cog", "act", "ref", "cre", "sdi", "is_void", "created_at")
    list_filter = ("cut", "is_void")
    search_fields = ("user__email",)
    readonly_fields = ("user", "cut", "mot", "cog", "act", "ref", "cre", "sdi",
                       "weights_json", "source", "created_at")
    actions = ["void_selected"]

    def has_add_permission(self, request):
        return False

    @admin.action(description="Tanlangan o'lchovlarni bekor qilish (void)")
    def void_selected(self, request, queryset):
        count = 0
        for measurement in queryset.filter(is_void=False):
            measurement.void("Admin tomonidan bekor qilindi")
            count += 1
        self.message_user(request, f"{count} ta o'lchov bekor qilindi.")


admin.site.register(Answer)
admin.site.register(Recommendation)
