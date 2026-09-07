"""
accounts — foydalanuvchi, profil, o'quv guruhi (TZ 4/M1, 6.2).
"""

import secrets
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
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


class StudyGroup(SoftDeleteModel):
    """
    O'quv guruhi (FR-03) + tadqiqot bo'linmasi (FR-04, FR-58).

    `study_arm` faqat admin/tadqiqotchiga ko'rinadi — talaba uni bilmaydi.
    """

    name = models.CharField("guruh nomi", max_length=120)
    otm = models.CharField("OTM", max_length=200, blank=True)
    faculty = models.CharField("fakultet", max_length=200, blank=True)
    course = models.PositiveSmallIntegerField("kurs", default=1)
    invite_code = models.CharField("guruh kodi", max_length=12, unique=True, blank=True)
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="led_groups", verbose_name="mentor",
    )
    study_arm = models.CharField(
        "tadqiqot guruhi", max_length=1, choices=StudyArm.choices, default=StudyArm.NONE,
    )
    is_active = models.BooleanField("faol", default=True)

    class Meta:
        verbose_name = "o'quv guruhi"
        verbose_name_plural = "o'quv guruhlari"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self._generate_code()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_code():
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # chalkash belgilar olib tashlangan
        while True:
            code = "".join(secrets.choice(alphabet) for _ in range(8))
            if not StudyGroup.all_objects.filter(invite_code=code).exists():
                return code

    @property
    def student_count(self):
        return self.enrollments.filter(is_active=True).count()


class Profile(SoftDeleteModel):
    """FR-02 — talaba/mentor profili va roli."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField("rol", max_length=20, choices=Role.choices, default=Role.STUDENT)
    otm = models.CharField("OTM", max_length=200, blank=True)
    faculty = models.CharField("fakultet", max_length=200, blank=True)
    course = models.PositiveSmallIntegerField("kurs", null=True, blank=True)
    group = models.ForeignKey(
        StudyGroup, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="profiles", verbose_name="guruh",
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
    def is_student(self):
        return self.role == Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == Role.TEACHER

    @property
    def is_researcher(self):
        return self.role == Role.RESEARCHER

    @property
    def is_methodist(self):
        return self.role == Role.METHODIST

    @property
    def is_manager(self):
        """Kontent yoki tizimni boshqara oladigan rollar."""
        return self.role in {Role.ADMIN, Role.METHODIST} or self.user.is_superuser

    @property
    def study_arm(self):
        return self.group.study_arm if self.group else StudyArm.NONE

    @property
    def mentor(self):
        return self.group.teacher if self.group else None

    def short_code(self):
        """Eksport va UI uchun qisqartirilgan anonim kod."""
        return str(self.respondent_id)[:8].upper()

    def give_consent(self):
        self.research_consent = True
        self.research_consent_at = timezone.now()
        self.save(update_fields=["research_consent", "research_consent_at", "updated_at"])


class Enrollment(SoftDeleteModel):
    """Talabaning guruhga a'zoligi (FR-03)."""

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name="enrollments")
    joined_at = models.DateTimeField("qo'shilgan", default=timezone.now)
    is_active = models.BooleanField("faol", default=True)

    class Meta:
        verbose_name = "guruh a'zoligi"
        verbose_name_plural = "guruh a'zoliklari"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "group"],
                condition=models.Q(is_deleted=False),
                name="uniq_active_enrollment",
            )
        ]

    def __str__(self):
        return f"{self.student} → {self.group}"


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
