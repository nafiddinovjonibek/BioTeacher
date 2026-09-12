from django.contrib import admin

from .models import (
    Assignment,
    CompetencyCheck,
    CompetencyItem,
    Criterion,
    AssignedTask,
    Rubric,
    Score,
    Submission,
    SubmissionFile,
)


class CriterionInline(admin.TabularInline):
    model = Criterion
    extra = 3


@admin.register(Rubric)
class RubricAdmin(admin.ModelAdmin):
    list_display = ("title", "criteria_count", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CriterionInline]

    @admin.display(description="mezonlar")
    def criteria_count(self, obj):
        return obj.criteria.count()


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "kind", "component", "bloom_level", "difficulty", "is_active")
    list_filter = ("module", "kind", "component", "bloom_level", "is_active")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "module", "kind", "is_active")}),
        ("Mazmun", {"fields": ("context_note", "body", "reference_solution")}),
        ("Ilmiy tasnif", {"fields": ("component", "bloom_level", "difficulty", "rubric")}),
        ("Sozlamalar", {"fields": ("estimated_minutes", "allow_files")}),
    )


class ScoreInline(admin.TabularInline):
    model = Score
    extra = 0
    readonly_fields = ("criterion", "scorer", "value", "author")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "student", "status", "self_percent", "mentor_percent", "submitted_at")
    list_filter = ("status", "assignment__module")
    search_fields = ("student__email", "assignment__title")
    readonly_fields = ("payload", "submitted_at", "graded_at")
    inlines = [ScoreInline]


@admin.register(CompetencyItem)
class CompetencyItemAdmin(admin.ModelAdmin):
    list_display = ("title", "component", "order", "is_active")
    list_filter = ("component", "is_active")


admin.site.register(Criterion)
admin.site.register(SubmissionFile)
admin.site.register(AssignedTask)
admin.site.register(CompetencyCheck)
