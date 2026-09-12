"""
accounts — foydalanuvchi va profil (TZ 4/M1, 6.2).
"""

import secrets
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from core.enums import Role, StudyArm
from core.models import SoftDeleteModel, TimeStampedModel


class UserManager(BaseUserManager):
    """FR-01 — email asosiy identifikator."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Email manzil kiritilishi shart.")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_active", True)
        extra.setdefault("email_verified", True)
        if extra.get("is_staff") is not True or extra.get("is_superuser") is not True:
            raise ValueError("Superuser is_staff va is_superuser=True bo'lishi kerak.")
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    """FR-01 — email/parol autentifikatsiyasi, email tasdiqlash."""

    email = models.EmailField("email", unique=True)
    email_verified = models.BooleanField("email tasdiqlangan", default=False)
    last_login_ip = models.GenericIPAddressField("oxirgi IP", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "foydalanuvchi"
        verbose_name_plural = "foydalanuvchilar"

    def __str__(self):
        return self.get_full_name() or self.email

    def get_short_name(self):
        return self.first_name or self.email.split("@")[0]

    def save(self, *args, **kwargs):
        # `username` AbstractUser'da unikal — email bilan ro'yxatdan o'tishda uni
        # avtomatik to'ldiramiz, aks holda bo'sh qiymatlar to'qnashadi.
        if not self.username:
            base = (self.email or "").split("@")[0][:140] or "user"
            candidate, suffix = base, 1
            while User.objects.filter(username=candidate).exclude(pk=self.pk).exists():
                suffix += 1
                candidate = f"{base}{suffix}"[:150]
            self.username = candidate
        super().save(*args, **kwargs)


class EmailVerification(TimeStampedModel):
    """FR-01 — email tasdiqlash tokeni."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_tokens")
    token = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "email tasdiqlash"
        verbose_name_plural = "email tasdiqlashlar"

    @property
    def is_valid(self):
        return self.used_at is None and (timezone.now() - self.created_at).days < 3

    def confirm_url(self):
        return reverse("accounts:verify_email", args=[self.token])


class Profile(SoftDeleteModel):
    """FR-02 — foydalanuvchi profili va roli."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    # `role` — hozir FAOL rol (barcha ruxsat tekshiruvlari shunga qaraydi).
    # `roles` — foydalanuvchiga berilgan barcha rollar, vergul bilan: "TEACHER,ADMIN".
    # Bir nechta rol bo'lsa, foydalanuvchi ular orasida almashib ishlaydi.
    role = models.CharField("faol rol", max_length=20, choices=Role.choices, default=Role.TEACHER)
    roles = models.CharField("berilgan rollar", max_length=100, blank=True, default="")
    otm = models.CharField("OTM", max_length=200, blank=True)
    faculty = models.CharField("fakultet", max_length=200, blank=True)
    course = models.PositiveSmallIntegerField("kurs", null=True, blank=True)
    study_arm = models.CharField(
        "tadqiqot bo'linmasi", max_length=1, choices=StudyArm.choices, default=StudyArm.NONE,
    )
    phone = models.CharField("telefon", max_length=32, blank=True)
    avatar = models.ImageField("avatar", upload_to="avatars/%Y/%m/", blank=True)
    bio = models.TextField("qisqacha", blank=True)

    # NFR-17 — ilmiy tadqiqotda ishtirok etishga rozilik.
    research_consent = models.BooleanField("tadqiqotda ishtirok roziligi", default=False)
    research_consent_at = models.DateTimeField(null=True, blank=True)

    # FR-60 — eksportda F.I.Sh. o'rniga ishlatiladigan barqaror identifikator.
    respondent_id = models.UUIDField("respondent ID", default=uuid.uuid4, unique=True, editable=False)

    onboarding_done = models.BooleanField("onboarding tugallangan", default=False)

    class Meta:
        verbose_name = "profil"
        verbose_name_plural = "profillar"

    def __str__(self):
        return f"{self.user} — {self.get_role_display()}"

    # --- Rol yordamchilari (shablonlarda ishlatiladi) ---
    @property
    def role_list(self):
        """Berilgan rollar (Role tartibida). Faol rol va superuser uchun ADMIN doim kiradi."""
        granted = {r.strip() for r in self.roles.split(",") if r.strip()}
        granted.add(self.role)
        if self.user.is_superuser:
            granted.add(Role.ADMIN)
        return [r for r in Role.values if r in granted]

    @property
    def role_choices(self):
        """Almashtirish menyusi uchun: [(kod, nomi), ...]."""
        return [(r, Role(r).label) for r in self.role_list]

    @property
    def has_multiple_roles(self):
        return len(self.role_list) > 1

    def has_granted_role(self, role):
        return role in self.role_list

    def set_roles(self, roles, active=None):
        """Berilgan rollarni saqlaydi; faol rol ro'yxatda bo'lmasa — birinchisi faol bo'ladi."""
        roles = [r for r in Role.values if r in set(roles)] or [Role.TEACHER]
        self.roles = ",".join(roles)
        if active in roles:
            self.role = active
        elif self.role not in roles:
            self.role = roles[0]

    def switch_role(self, role):
        """Faol rolni almashtiradi. Berilmagan rolga o'tib bo'lmaydi."""
        if not self.has_granted_role(role):
            return False
        self.role = role
        self.save(update_fields=["role", "updated_at"])
        return True

    @property
    def is_teacher(self):
        """Faol rol — o'rganuvchi (o'qituvchi) rejimi."""
        return self.role == Role.TEACHER

    @property
    def is_admin(self):
        """Faol rol — administrator rejimi."""
        return self.role == Role.ADMIN

    @property
    def is_manager(self):
        """Kontent yoki tizimni boshqara oladigan rol (CRUD)."""
        return self.is_admin

    def short_code(self):
        """Eksport va UI uchun qisqartirilgan anonim kod."""
        return str(self.respondent_id)[:8].upper()

    def give_consent(self):
        self.research_consent = True
        self.research_consent_at = timezone.now()
        self.save(update_fields=["research_consent", "research_consent_at", "updated_at"])


class MenuItem(models.Model):
    """
    Yon panel bandi yoki ichki bandi (`parent` berilsa).

    Band yo sahifaga (`page` — `accounts.menu.PAGES` kaliti yoki `section:<slug>`),
    yo ixtiyoriy havolaga (`url`) ulanadi.
    """

    key = models.CharField("band kaliti", max_length=60, unique=True)
    group = models.ForeignKey(
        "MenuGroup", on_delete=models.CASCADE, null=True, related_name="items", verbose_name="blok",
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children",
        verbose_name="ota band",
    )
    order = models.PositiveSmallIntegerField("tartib", default=0)
    label = models.CharField("nom", max_length=60, blank=True, help_text="Bo'sh — sahifaning standart nomi.")
    page = models.CharField("sahifa", max_length=60, blank=True)
    url = models.CharField("havola", max_length=300, blank=True)
    icon = models.CharField("ikonka", max_length=20, blank=True, help_text="Bo'sh — sahifa ikonkasi.")
    hint = models.CharField("izoh", max_length=60, blank=True)

    class Meta:
        verbose_name = "menyu bandi"
        verbose_name_plural = "menyu bandlari"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.key} → {self.order}"


class MenuGroup(models.Model):
    """Yon panel bloki (guruhi): sarlavha, tartib va kimning menyusi."""

    class Audience(models.TextChoices):
        TEACHER = "teacher", "O'qituvchi menyusi"
        ADMIN = "admin", "Admin menyusi"

    key = models.CharField("guruh kaliti", max_length=30, unique=True)
    order = models.PositiveSmallIntegerField("tartib", null=True, blank=True)
    # None — standart sarlavha; "" — sarlavha ko'rsatilmaydi.
    title = models.CharField("sarlavha", max_length=60, null=True, blank=True)
    audience = models.CharField("menyu", max_length=8, choices=Audience.choices, default=Audience.TEACHER)

    class Meta:
        verbose_name = "menyu guruhi"
        verbose_name_plural = "menyu guruhlari"
        ordering = ["order", "id"]

    def __str__(self):
        return self.key


class AuditLog(models.Model):
    """NFR-14 — kim, qachon, nimani o'zgartirdi."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="audit_entries",
    )
    action = models.CharField("harakat", max_length=80, db_index=True)
    target = models.CharField("obyekt", max_length=200, blank=True)
    detail = models.JSONField("tafsilot", default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "audit yozuvi"
        verbose_name_plural = "audit jurnali"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.action}"


def has_role_q(role, prefix="profile__"):
    """Faol yoki berilgan rollari orasida `role` bo'lgan profillar uchun Q-filtr."""
    return Q(**{f"{prefix}role": role}) | Q(**{f"{prefix}roles__contains": role})
