"""accounts view'lari: kirish, ro'yxat, profil, onboarding (FR-01..FR-06)."""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from core.enums import Cut

from .forms import JoinGroupForm, LoginForm, ProfileForm, RegisterForm
from .models import EmailVerification, Enrollment, StudyGroup
from .services import (
    clear_login_attempts,
    client_ip,
    is_login_blocked,
    log_action,
    login_attempts_left,
    register_failed_login,
    send_verification_email,
)


def register(request):
    if request.user.is_authenticated:
        return redirect("home:dashboard")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        send_verification_email(request, user)
        login(request, user, backend="accounts.backends.EmailOrUsernameBackend")
        log_action(request, "user.register", user.email)
        messages.success(
            request,
            "Ro'yxatdan o'tdingiz. Email manzilingizga tasdiqlash havolasi yuborildi.",
        )
        return redirect("accounts:onboarding")
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home:dashboard")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        identifier = form.cleaned_data["email"].strip().lower()
        ip = client_ip(request)

        # NFR-09 — email va IP bo'yicha alohida cheklov.
        if is_login_blocked(identifier) or is_login_blocked(f"ip:{ip}"):
            messages.error(
                request,
                "Juda ko'p urinish qilindi. Xavfsizlik uchun 15 daqiqadan keyin qayta urinib ko'ring.",
            )
            return render(request, "accounts/login.html", {"form": form})

        from django.contrib.auth import authenticate

        user = authenticate(
            request, username=identifier, password=form.cleaned_data["password"]
        )
        if user is None:
            register_failed_login(identifier)
            register_failed_login(f"ip:{ip}")
            left = login_attempts_left(identifier)
            log_action(request, "user.login_failed", identifier)
            messages.error(
                request,
                f"Email yoki parol noto'g'ri. Qolgan urinishlar: {left}.",
            )
            return render(request, "accounts/login.html", {"form": form})

        clear_login_attempts(identifier)
        clear_login_attempts(f"ip:{ip}")
        login(request, user)
        user.last_login_ip = ip
        user.save(update_fields=["last_login_ip"])
        if not form.cleaned_data.get("remember"):
            request.session.set_expiry(0)
        log_action(request, "user.login", user.email)
        return redirect(request.GET.get("next") or "home:dashboard")

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    log_action(request, "user.logout", request.user.email)
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect("home:landing")


def verify_email(request, token):
    """FR-01 — email tasdiqlash."""
    verification = EmailVerification.objects.filter(token=token).select_related("user").first()
    if verification is None or not verification.is_valid:
        messages.error(request, "Havola yaroqsiz yoki muddati o'tgan. Qaytadan so'rang.")
        return redirect("accounts:login")

    verification.used_at = timezone.now()
    verification.save(update_fields=["used_at", "updated_at"])
    user = verification.user
    user.email_verified = True
    user.save(update_fields=["email_verified"])
    log_action(request, "user.email_verified", user.email)
    messages.success(request, "Email manzilingiz tasdiqlandi.")
    return redirect("home:dashboard" if request.user.is_authenticated else "accounts:login")


@login_required
def resend_verification(request):
    if request.user.email_verified:
        messages.info(request, "Email allaqachon tasdiqlangan.")
    else:
        send_verification_email(request, request.user)
        messages.success(request, "Tasdiqlash havolasi qayta yuborildi.")
    return redirect("accounts:onboarding")


@login_required
def onboarding(request):
    """
    FR-06 — bloklanadigan onboarding.

    3 qadam: profil → guruh → boshlang'ich diagnostika.
    """
    from diagnostics.models import Questionnaire

    profile = request.user.profile
    questionnaires = Questionnaire.objects.filter(cut=Cut.INITIAL, is_active=True).order_by("kind")
    done_slugs = set(
        request.user.attempts.filter(status="FINISHED").values_list(
            "questionnaire__slug", flat=True
        )
    )
    steps = [
        {
            "title": "Profilingizni to'ldiring",
            "done": bool(profile.otm and request.user.first_name),
            "url": "accounts:profile_edit",
            "cta": "Profilni to'ldirish",
        },
        {
            "title": "Guruhga qo'shiling",
            "done": profile.group is not None,
            "url": "accounts:join_group",
            "cta": "Guruh kodini kiritish",
            "optional": True,
        },
    ]
    return render(
        request,
        "accounts/onboarding.html",
        {
            "steps": steps,
            "questionnaires": questionnaires,
            "done_slugs": done_slugs,
            "profile": profile,
        },
    )


@login_required
def profile_edit(request):
    profile = request.user.profile
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "profile.update", request.user.email)
        messages.success(request, "Profil yangilandi.")
        return redirect("accounts:onboarding" if not profile.onboarding_done else "home:cabinet")
    return render(request, "accounts/profile_edit.html", {"form": form})


@login_required
def join_group(request):
    """FR-03 — guruh kodi orqali qo'shilish."""
    form = JoinGroupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        group = form.group
        profile = request.user.profile
        profile.group = group
        profile.otm = profile.otm or group.otm
        profile.faculty = profile.faculty or group.faculty
        profile.course = profile.course or group.course
        profile.save()
        Enrollment.objects.get_or_create(student=request.user, group=group)
        log_action(request, "group.join", group.name)
        messages.success(request, f"\"{group.name}\" guruhiga qo'shildingiz.")
        return redirect("accounts:onboarding" if not profile.onboarding_done else "home:cabinet")
    return render(request, "accounts/join_group.html", {"form": form})


@login_required
def consent(request):
    """NFR-17 — tadqiqotda ishtirok etishga rozilik."""
    if request.method == "POST":
        if request.POST.get("agree") == "1":
            request.user.profile.give_consent()
            log_action(request, "research.consent", request.user.email)
            messages.success(request, "Rozilik qayd etildi. Rahmat!")
        else:
            profile = request.user.profile
            profile.research_consent = False
            profile.save(update_fields=["research_consent", "updated_at"])
            messages.info(request, "Rozilik bekor qilindi. Bu platformadan foydalanishga to'sqinlik qilmaydi.")
        return redirect("home:cabinet")
    return render(request, "accounts/consent.html")


# --- Parolni tiklash (FR-05) ---

class PasswordResetView(auth_views.PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/email/password_reset.txt"
    subject_template_name = "accounts/email/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
