from django.contrib import admin

from .models import ActivityLog, ComponentScore, DailyTask, ProgressSnapshot, Streak


@admin.register(ComponentScore)
class ComponentScoreAdmin(admin.ModelAdmin):
    list_display = ("user", "component", "value", "diagnostic_part", "practice_part", "sample_size")
    list_filter = ("component",)
    search_fields = ("user__email",)


@admin.register(ProgressSnapshot)
class ProgressSnapshotAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "mot", "cog", "act", "ref", "cre", "sdi")
    list_filter = ("date",)
    search_fields = ("user__email",)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "object_ref", "created_at")
    list_filter = ("action",)
    search_fields = ("user__email", "object_ref")


admin.site.register(Streak)
admin.site.register(DailyTask)
