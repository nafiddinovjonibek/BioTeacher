"""accounts yordamchi servislari: audit, IP, email, login rate-limit."""

import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

from .models import AuditLog, EmailVerification

audit_logger = logging.getLogger("bioteacher.audit")


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_action(request, action, target="", **detail):
    """NFR-14 — audit yozuvi (bazaga + faylga)."""
    user = getattr(request, "user", None)
    actor = user if getattr(user, "is_authenticated", False) else None
    ip = client_ip(request) if request else None
    AuditLog.objects.create(actor=actor, action=action, target=str(target), detail=detail, ip=ip)
    audit_logger.info("%s | actor=%s | target=%s | %s", action, actor, target, detail)


# --- NFR-09: login urinishlarini cheklash ---

def _rl_key(identifier):
    return f"login-attempts:{identifier}"


def login_attempts_left(identifier):
    attempts = cache.get(_rl_key(identifier), [])
    window = settings.LOGIN_RATELIMIT_WINDOW_SECONDS
    now = time.time()
    attempts = [t for t in attempts if now - t < window]
    return max(0, settings.LOGIN_RATELIMIT_ATTEMPTS - len(attempts))


def register_failed_login(identifier):
    key = _rl_key(identifier)
    window = settings.LOGIN_RATELIMIT_WINDOW_SECONDS
    now = time.time()
    attempts = [t for t in cache.get(key, []) if now - t < window]
    attempts.append(now)
    cache.set(key, attempts, window)


def clear_login_attempts(identifier):
    cache.delete(_rl_key(identifier))


def is_login_blocked(identifier):
    return login_attempts_left(identifier) <= 0


# --- Email ---

def send_verification_email(request, user):
    """FR-01 — tasdiqlash havolasini yuborish."""
    token = EmailVerification.objects.create(user=user)
    link = request.build_absolute_uri(reverse("accounts:verify_email", args=[token.token]))
    body = render_to_string("accounts/email/verify.txt", {"user": user, "link": link})
    send_mail(
        subject=f"{settings.SITE_NAME} — email manzilingizni tasdiqlang",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
    return token
