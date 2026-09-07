"""accounts formalari (FR-01..FR-05)."""

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.utils import timezone

from core.enums import Role

from .models import Enrollment, Profile, StudyGroup

User = get_user_model()

INPUT_CLASS = (
    "w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-slate-900 "
    "placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 "
    "focus:outline-none transition"
)
SELECT_CLASS = INPUT_CLASS
TEXTAREA_CLASS = INPUT_CLASS + " min-h-[120px]"


class StyledFormMixin:
    """Barcha maydonlarga bir xil Tailwind sinflarini beradi."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                continue
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("class", TEXTAREA_CLASS)
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", SELECT_CLASS)
            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs.setdefault("class", "w-full text-sm text-slate-600")
            else:
                widget.attrs.setdefault("class", INPUT_CLASS)


class RegisterForm(StyledFormMixin, forms.Form):
    """FR-01, FR-02, FR-03 — ro'yxatdan o'tish + guruh kodi."""

    first_name = forms.CharField(label="Ism", max_length=80)
    last_name = forms.CharField(label="Familiya", max_length=80)
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(label="Parol", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Parolni takrorlang", widget=forms.PasswordInput)
    invite_code = forms.CharField(
        label="Guruh kodi", max_length=12, required=False,
        help_text="Mentoringiz bergan kod. Keyinroq ham kiritishingiz mumkin.",
    )
    consent = forms.BooleanField(
        label="Ilmiy tadqiqotda anonim ishtirok etishga roziman",
        required=False,
        help_text="Ma'lumotlaringiz faqat ilmiy maqsadda, ismsiz ko'rinishda ishlatiladi.",
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return email

    def clean_invite_code(self):
        code = (self.cleaned_data.get("invite_code") or "").strip().upper()
        if not code:
            return ""
        if not StudyGroup.objects.filter(invite_code=code, is_active=True).exists():
            raise forms.ValidationError("Bunday guruh kodi topilmadi.")
        return code

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Parollar mos kelmadi.")
        elif p1:
            password_validation.validate_password(p1)
        return cleaned

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            email=data["email"],
            password=data["password1"],
            first_name=data["first_name"].strip(),
            last_name=data["last_name"].strip(),
        )
        profile = user.profile
        profile.role = Role.STUDENT
        if data.get("consent"):
            profile.research_consent = True
            profile.research_consent_at = timezone.now()
        code = data.get("invite_code")
        if code:
            group = StudyGroup.objects.filter(invite_code=code, is_active=True).first()
            if group:
                profile.group = group
                profile.otm = group.otm
                profile.faculty = group.faculty
                profile.course = group.course
                Enrollment.objects.get_or_create(student=user, group=group)
        profile.save()
        return user


class LoginForm(StyledFormMixin, forms.Form):
    email = forms.CharField(label="Email")
    password = forms.CharField(label="Parol", widget=forms.PasswordInput)
    remember = forms.BooleanField(label="Meni eslab qol", required=False)


class ProfileForm(StyledFormMixin, forms.ModelForm):
    """FR-02 — profil tahriri."""

    first_name = forms.CharField(label="Ism", max_length=80)
    last_name = forms.CharField(label="Familiya", max_length=80)

    class Meta:
        model = Profile
        fields = ["otm", "faculty", "course", "phone", "avatar", "bio"]
        labels = {
            "otm": "OTM", "faculty": "Fakultet", "course": "Kurs",
            "phone": "Telefon", "avatar": "Avatar", "bio": "Qisqacha o'zingiz haqingizda",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = self.instance.user.first_name
        self.fields["last_name"].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        if commit:
            user.save(update_fields=["first_name", "last_name"])
            profile.save()
        return profile


class JoinGroupForm(StyledFormMixin, forms.Form):
    """FR-03 — guruhga kod orqali qo'shilish."""

    invite_code = forms.CharField(label="Guruh kodi", max_length=12)

    def clean_invite_code(self):
        code = self.cleaned_data["invite_code"].strip().upper()
        group = StudyGroup.objects.filter(invite_code=code, is_active=True).first()
        if group is None:
            raise forms.ValidationError("Bunday guruh kodi topilmadi yoki guruh faol emas.")
        self.group = group
        return code


class StudyGroupForm(StyledFormMixin, forms.ModelForm):
    """Mentor uchun guruh yaratish/tahrirlash (study_arm bu yerda YO'Q — FR-04)."""

    class Meta:
        model = StudyGroup
        fields = ["name", "otm", "faculty", "course", "is_active"]
        labels = {
            "name": "Guruh nomi", "otm": "OTM", "faculty": "Fakultet",
            "course": "Kurs", "is_active": "Faol",
        }
