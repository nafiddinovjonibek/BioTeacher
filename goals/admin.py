from django.contrib import admin

from .models import Goal, GoalTask


class GoalTaskInline(admin.TabularInline):
    model = GoalTask
    extra = 0


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "component", "status", "deadline", "mentor_approved")
    list_filter = ("status", "component", "mentor_approved")
    search_fields = ("title", "user__email")
    inlines = [GoalTaskInline]
