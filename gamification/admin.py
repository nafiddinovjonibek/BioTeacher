from django.contrib import admin

from .models import Badge, BadgeRule, UserBadge


class BadgeRuleInline(admin.TabularInline):
    model = BadgeRule
    extra = 1


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("emoji", "title", "code", "order", "is_active")
    prepopulated_fields = {"code": ("title",)}
    inlines = [BadgeRuleInline]


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge", "created_at")
    search_fields = ("user__email",)
