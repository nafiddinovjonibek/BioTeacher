"""Topshiriq formalari: bosqichli javob, o'zini baholash, mentor bahosi, fayl."""

from django import forms
from django.conf import settings

from accounts.forms import INPUT_CLASS, StyledFormMixin, TEXTAREA_CLASS

from .models import Submission, SubmissionFile

MIN_STEP_LENGTH = 60  # bosqich javobining minimal hajmi


class StepAnswerForm(forms.Form):
    """
    FR-22/FR-23/FR-28/FR-29 — topshiriq bosqichlari dinamik ravishda maydonga aylanadi.
    """

    def __init__(self, *args, assignment=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.assignment = assignment
        for key, label, hint in assignment.steps():
            self.fields[key] = forms.CharField(
                label=label,
                help_text=hint,
                required=False,
                widget=forms.Textarea(
                    attrs={"class": TEXTAREA_CLASS, "rows": 5, "placeholder": hint}
                ),
            )

    def clean(self):
        cleaned = super().clean()
        if self.data.get("action") == "submit":
            for key, label, _ in self.assignment.steps():
                text = (cleaned.get(key) or "").strip()
                if len(text) < MIN_STEP_LENGTH:
                    self.add_error(
                        key,
                        f"\"{label}\" bo'limini to'ldiring — kamida {MIN_STEP_LENGTH} belgi.",
                    )
        return cleaned


class SelfAssessmentForm(forms.Form):
    """FR-25 — foydalanuvchi rubrika bo'yicha o'zini baholaydi."""

    def __init__(self, *args, rubric=None, initial_scores=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.rubric = rubric
        initial_scores = initial_scores or {}
        for criterion in rubric.criteria.all():
            self.fields[f"c{criterion.id}"] = forms.ChoiceField(
                label=criterion.name,
                help_text=criterion.hint,
                choices=[
                    (i, f"{i} — {criterion.level_descriptions.get(str(i), '')}".rstrip(" —"))
                    for i in criterion.scale()
                ],
                initial=initial_scores.get(criterion.id),
                widget=forms.RadioSelect,
            )

    def scores(self):
        return {
            key[1:]: int(value) for key, value in self.cleaned_data.items() if key.startswith("c")
        }


class MentorGradeForm(SelfAssessmentForm):
    """FR-55 — mentor bahosi + matnli fikr-mulohaza."""

    feedback = forms.CharField(
        label="Fikr-mulohaza",
        widget=forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 5}),
        help_text="Nima yaxshi bajarilgan va aynan nimani yaxshilash kerak.",
    )

    def scores(self):
        return {
            key[1:]: int(value)
            for key, value in self.cleaned_data.items()
            if key.startswith("c") and key != "feedback"
        }


class SubmissionFileForm(forms.ModelForm):
    """NFR-11 — fayl turi va hajmi validatsiyasi."""

    class Meta:
        model = SubmissionFile
        fields = ["file"]
        labels = {"file": "Fayl biriktirish"}

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        limit = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if uploaded.size > limit:
            raise forms.ValidationError(
                f"Fayl hajmi {settings.MAX_UPLOAD_SIZE_MB} MB dan oshmasligi kerak."
            )
        name = uploaded.name.lower()
        if not any(name.endswith(ext) for ext in settings.ALLOWED_UPLOAD_EXTENSIONS):
            allowed = ", ".join(settings.ALLOWED_UPLOAD_EXTENSIONS)
            raise forms.ValidationError(f"Ruxsat etilgan formatlar: {allowed}")
        return uploaded


class GalleryConsentForm(forms.ModelForm):
    """FR-36 — ijodiy galereyaga chiqarishga rozilik."""

    class Meta:
        model = Submission
        fields = ["is_public"]
        labels = {"is_public": "Ishimni boshqa o'qituvchilar ko'rishi mumkin"}


class AssignTaskForm(StyledFormMixin, forms.Form):
    """FR-57 — o'qituvchilarga topshiriq tayinlash."""

    assignment = forms.ModelChoiceField(
        label="Topshiriq", queryset=None, empty_label="— tanlang —"
    )
    deadline = forms.DateTimeField(
        label="Muddat", required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": INPUT_CLASS}),
    )
    note = forms.CharField(
        label="Izoh", required=False,
        widget=forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Assignment

        self.fields["assignment"].queryset = Assignment.objects.filter(is_active=True)
