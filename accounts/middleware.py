"""
FR-06 — ro'yxatdan o'tgan o'qituvchi boshlang'ich diagnostikadan o'tmaguncha
platformaning qolgan qismi bloklanadi (bloklanadigan onboarding).
"""

from django.shortcuts import redirect
from django.urls import resolve, reverse

from core.enums import Role

# Onboarding tugamagan foydalanuvchi ham kira oladigan url nomlari.
ALLOWED_URL_NAMES = {
    "accounts:login",
    "accounts:logout",
    "accounts:register",
    "accounts:verify_email",
    "accounts:resend_verification",
    "accounts:password_reset",
    "accounts:password_reset_done",
    "accounts:password_reset_confirm",
    "accounts:password_reset_complete",
    "accounts:onboarding",
    "accounts:profile_edit",
    "accounts:consent",
    "accounts:switch_role",
    "diagnostics:start",
    "diagnostics:take",
    "diagnostics:answer",
    "diagnostics:finish",
    "diagnostics:result",
    "home:landing",
    "home:cabinet",
    "home:about",
}

ALLOWED_PREFIXES = ("/admin/", "/static/", "/media/")


class OnboardingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated or user.is_superuser:
            return self.get_response(request)

        path = request.path
        if path.startswith(ALLOWED_PREFIXES):
            return self.get_response(request)

        profile = getattr(user, "profile", None)
        if profile is None or profile.role != Role.TEACHER or profile.onboarding_done:
            return self.get_response(request)

        try:
            match = resolve(path)
            url_name = f"{match.namespace}:{match.url_name}" if match.namespace else match.url_name
        except Exception:
            return self.get_response(request)

        if url_name in ALLOWED_URL_NAMES:
            return self.get_response(request)

        return redirect(reverse("accounts:onboarding"))
