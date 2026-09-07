from django.contrib import admin

from .models import ExportJob, StatSummary


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = ("created_at", "requested_by", "fmt", "row_count", "filename")
    readonly_fields = ("requested_by", "fmt", "cuts", "arms", "row_count", "filename", "created_at")

    def has_add_permission(self, request):
        return False


@admin.register(StatSummary)
class StatSummaryAdmin(admin.ModelAdmin):
    list_display = ("cut", "arm", "component", "n", "mean", "sd", "minimum", "maximum")
    list_filter = ("cut", "arm", "component")
