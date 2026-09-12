"""Boshqaruv paneli (CRUD) formalari."""

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.utils.text import slugify

from core.enums import Role, StudyArm

from .forms import StyledFormMixin
from .models import Profile

User = get_user_model()


def manage_formfield(db_field, **kwargs):
    """Sana/vaqt va JSON maydonlari uchun qulay vidjetlar."""
    field_type = db_field.get_internal_type()
    if field_type == "DateTimeField":
        kwargs.setdefault(
            "widget", forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M")
        )
    elif field_type == "DateField":
        kwargs.setdefault("widget", forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    elif field_type == "JSONField":
        kwargs.setdefault("widget", forms.Textarea(attrs={"rows": 4, "class": "font-mono text-sm"}))
    return db_field.formfield(**kwargs)


def _has_field(model, name):
    return any(f.name == name for f in model._meta.fields)


def unique_slug(model, base, exclude_pk=None):
    """Sarlavhadan slug yasaydi; band bo'lsa -2, -3 … qo'shadi."""
    manager = getattr(model, "all_objects", model._default_manager)
    base = slugify(base)[:60] or "yozuv"
    candidate, n = base, 1
    while manager.filter(slug=candidate).exclude(pk=exclude_pk).exists():
        n += 1
        candidate = f"{base}-{n}"
    return candidate


def next_order(instance):
    """
    Yangi yozuv uchun tartib raqami: o'z «ota» doirasida (masalan, mavzu ichidagi
    darslar) eng kattasidan keyingisi. Ota bo'lmasa — butun jadval bo'yicha.
    """
    model = type(instance)
    queryset = model._default_manager.all()
    for f in model._meta.fields:
        if f.many_to_one and getattr(instance, f.attname, None) is not None:
            queryset = queryset.filter(**{f.attname: getattr(instance, f.attname)})
            break
    last = queryset.order_by("-order").values_list("order", flat=True).first()
    return 0 if last is None else last + 1


class BaseManageForm(StyledFormMixin, forms.ModelForm):
    """
    Reyestrdagi har bir model uchun avtomatik quriladigan forma.

    `slug` va `order` formada ko'rsatilmaydi — saqlashda avtomatik to'ldiriladi:
    slug sarlavhadan (title/name), order — o'z doirasida oxirgi raqamdan keyingisi.
    """

    slug_from = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            if isinstance(f.widget, forms.Textarea):
                f.widget.attrs.setdefault("rows", 5)

    def _fill_auto_fields(self):
        obj = self.instance
        model = self._meta.model
        if _has_field(model, "slug") and not getattr(obj, "slug", ""):
            source = self.slug_from or ("title" if _has_field(model, "title") else "name")
            obj.slug = unique_slug(model, getattr(obj, source, "") or "", obj.pk)
        if _has_field(model, "order") and obj.pk is None and "order" not in self.fields:
            obj.order = next_order(obj)

    def save(self, commit=True):
        self._fill_auto_fields()
        return super().save(commit=commit)


class UserManageForm(StyledFormMixin, forms.ModelForm):
    """Foydalanuvchi + profil bitta formada (admin uchun)."""

    roles = forms.MultipleChoiceField(
        label="Rollar", choices=Role.choices, initial=[Role.TEACHER],
        widget=forms.CheckboxSelectMultiple,
        help_text="Bir nechta rol belgilansa, foydalanuvchi ular orasida almashib ishlaydi.",
    )
    role = forms.ChoiceField(
        label="Faol rol", choices=Role.choices, initial=Role.TEACHER,
        help_text="Kirganda qaysi rejimda ochilishi. Belgilangan rollardan biri bo'lishi kerak.",
    )
    otm = forms.CharField(label="OTM", max_length=200, required=False)
    faculty = forms.CharField(label="Fakultet", max_length=200, required=False)
    course = forms.IntegerField(label="Kurs", required=False, min_value=1, max_value=8)
    phone = forms.CharField(label="Telefon", max_length=32, required=False)
    study_arm = forms.ChoiceField(label="Tadqiqot bo'linmasi", choices=StudyArm.choices, required=False)
    research_consent = forms.BooleanField(label="Tadqiqotda ishtirok roziligi", required=False)
    onboarding_done = forms.BooleanField(label="Onboarding tugallangan", required=False)
    new_password = forms.CharField(
        label="Yangi parol", required=False, widget=forms.PasswordInput,
        help_text="Yangi foydalanuvchi uchun majburiy; mavjud foydalanuvchida bo'sh qoldirilsa o'zgarmaydi.",
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "is_active", "email_verified"]
        labels = {
            "email": "Email", "first_name": "Ism", "last_name": "Familiya",
            "is_active": "Faol", "email_verified": "Email tasdiqlangan",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = getattr(self.instance, "profile", None) if self.instance.pk else None
        if profile:
            for name in ["role", "otm", "faculty", "course", "phone", "study_arm",
                         "research_consent", "onboarding_done"]:
                self.fields[name].initial = getattr(profile, name)
            self.fields["roles"].initial = profile.role_list
        else:
            self.fields["email_verified"].initial = True

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Bu email allaqachon band.")
        return email

    def clean(self):
        cleaned = super().clean()
        roles, active = cleaned.get("roles") or [], cleaned.get("role")
        if roles and active and active not in roles:
            self.add_error("role", "Faol rol belgilangan rollar ichida bo'lishi kerak.")
        return cleaned

    def clean_new_password(self):
        password = self.cleaned_data.get("new_password") or ""
        if not self.instance.pk and not password:
            raise forms.ValidationError("Yangi foydalanuvchi uchun parol kiriting.")
        if password:
            password_validation.validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("new_password")
        if password:
            user.set_password(password)
        elif not user.pk:
            user.set_unusable_password()
        user.save()

        profile, _ = Profile.objects.get_or_create(user=user)
        for name in ["otm", "faculty", "phone", "research_consent", "onboarding_done"]:
            setattr(profile, name, self.cleaned_data.get(name))
        profile.set_roles(self.cleaned_data.get("roles") or [], active=self.cleaned_data.get("role"))
        profile.course = self.cleaned_data.get("course")
        profile.study_arm = self.cleaned_data.get("study_arm") or StudyArm.NONE
        profile.save()
        return user
