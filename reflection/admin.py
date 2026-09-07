from django.contrib import admin

from .models import ReflectionEntry, ReflectionPrompt


@admin.register(ReflectionPrompt)
class ReflectionPromptAdmin(admin.ModelAdmin):
    list_display = ("slot", "text", "is_active")
    list_filter = ("slot", "is_active")


@admin.register(ReflectionEntry)
class ReflectionEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "quality_score", "created_at")
    list_filter = ("kind",)
    search_fields = ("user__email", "q1", "q2", "q3", "q4", "free_text")
    readonly_fields = ("quality_detail",)
