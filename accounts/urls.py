from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "accounts"

urlpatterns = [
    path("kirish/", views.login_view, name="login"),
    path("chiqish/", views.logout_view, name="logout"),
    path("royxat/", views.register, name="register"),
    path("tasdiqlash/<str:token>/", views.verify_email, name="verify_email"),
    path("tasdiqlash/qayta/", views.resend_verification, name="resend_verification"),
    path("boshlash/", views.onboarding, name="onboarding"),
    # Eski manzil — kabinetga koʻchdi (2026-09, redesign).
    path("profil/", RedirectView.as_view(pattern_name="home:cabinet"), name="profile"),
    path("profil/tahrir/", views.profile_edit, name="profile_edit"),
    path("guruhga-qoshilish/", views.join_group, name="join_group"),
    path("rozilik/", views.consent, name="consent"),
    path("parol/tiklash/", views.PasswordResetView.as_view(), name="password_reset"),
    path("parol/tiklash/yuborildi/", views.PasswordResetDoneView.as_view(),
         name="password_reset_done"),
    path("parol/tiklash/<uidb64>/<token>/", views.PasswordResetConfirmView.as_view(),
         name="password_reset_confirm"),
    path("parol/tiklash/tugadi/", views.PasswordResetCompleteView.as_view(),
         name="password_reset_complete"),
]
