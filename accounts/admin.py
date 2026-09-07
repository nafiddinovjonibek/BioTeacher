from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuditLog, EmailVerification, Enrollment, Profile, StudyGroup, User


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0
    readonly_fields = ("respondent_id",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ("email", "first_name", "last_name", "email_verified", "is_staff", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active", "email_verified")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Shaxsiy", {"fields": ("first_name", "last_name", "username")}),
        ("Ruxsatlar", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Xizmat", {"fields": ("email_verified", "last_login", "last_login_ip", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    readonly_fields = ("last_login", "date_joined", "last_login_ip")


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "otm", "course", "teacher", "study_arm", "invite_code", "student_count", "is_active")
    list_filter = ("study_arm", "is_active", "course")
    search_fields = ("name", "otm", "invite_code")
    readonly_fields = ("invite_code",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "group", "course", "research_consent", "onboarding_done")
    list_filter = ("role", "research_consent", "onboarding_done", "group")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    readonly_fields = ("respondent_id",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "group", "joined_at", "is_active")
    list_filter = ("is_active", "group")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "action", "target", "ip")
    list_filter = ("action",)
    search_fields = ("action", "target", "actor__email")
    readonly_fields = ("actor", "action", "target", "detail", "ip", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(EmailVerification)
