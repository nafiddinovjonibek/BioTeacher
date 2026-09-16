"""
Boshqaruv paneli uchun CRUD reyestri.

Har bir model bitta `ModelConfig` bilan ro'yxatga olinadi; `views_crud` shu
konfiguratsiya asosida ro'yxat / yaratish / tahrirlash / o'chirish sahifalarini
avtomatik quradi. Yangi model qo'shish = bitta yozuv qo'shish.
"""

from dataclasses import dataclass, field

from django.contrib.auth import get_user_model

from core.models import SoftDeleteModel

User = get_user_model()


@dataclass
class ModelConfig:
    key: str
    model: type
    group: str
    title: str = ""                       # bo'sh bo'lsa — verbose_name_plural
    singular_label: str = ""              # bo'sh bo'lsa — verbose_name
    icon: str = "book"
    base_filter: dict = field(default_factory=dict)   # bitta model — bir nechta bo'lim
    base_exclude: dict = field(default_factory=dict)  # (masalan: testlar / anketalar)
    fields: list | None = None            # None → barcha tahrirlanadigan maydonlar
    columns: list = field(default_factory=list)   # [(sarlavha, accessor)]
    search: list = field(default_factory=list)    # icontains lookup'lar
    filters: list = field(default_factory=list)   # GET orqali ruxsat etilgan filtrlar
    children: list = field(default_factory=list)  # [(yorliq, child_key, fk_nomi)]
    ordering: list | None = None
    select_related: list = field(default_factory=list)
    can_add: bool = True
    can_edit: bool = True
    can_delete: bool = True
    delete_mode: str = "default"          # "default" | "void" (Measurement)
    slug_from: str | None = None          # slug bo'sh bo'lsa shu maydondan quriladi
    form_class: type | None = None
    note: str = ""                        # sahifa tepasidagi izoh
    builder_kind: str | None = None       # sodda quruvchi (accounts.builders) mavjud bo'lsa
    builder_query: str = ""               # quruvchiga uzatiladigan query (masalan: "?kind=TEST")
    defaults: dict = field(default_factory=dict)       # yangi yozuvga formada ko'rinmaydigan qiymatlar
    initial: object = None                # callable(filters) -> dict: formaning boshlang'ich qiymatlari
    limit_choices: dict = field(default_factory=dict)  # {maydon: [ruxsat etilgan qiymatlar]}
    site_url: str = ""                    # yozuvlar saytda ko'rinadigan sahifa (url nomi)

    @property
    def label(self):
        return self.title or str(self.model._meta.verbose_name_plural).capitalize()

    @property
    def singular(self):
        return self.singular_label or str(self.model._meta.verbose_name)

    @property
    def soft_delete(self):
        return issubclass(self.model, SoftDeleteModel)

    @property
    def orderable(self):
        """`order` maydoni bor modellar ro'yxatda drag & drop bilan tartiblanadi."""
        return any(f.name == "order" for f in self.model._meta.fields)

    def base_queryset(self, deleted=False):
        if self.soft_delete:
            qs = self.model.all_objects.filter(is_deleted=deleted)
        else:
            qs = self.model.objects.all()
        if self.base_filter:
            qs = qs.filter(**self.base_filter)
        if self.base_exclude:
            qs = qs.exclude(**self.base_exclude)
        if self.select_related:
            qs = qs.select_related(*self.select_related)
        if self.ordering:
            qs = qs.order_by(*self.ordering)
        elif not self.model._meta.ordering:
            qs = qs.order_by("-pk")  # sahifalash barqaror bo'lishi uchun
        return qs


GROUPS = [
    ("kontent", "Kontent (BioBilim)", "book"),
    ("rivojlantirish", "3-blok: O‘z-o‘zini rivojlantirish", "sprout"),
    ("diagnostika", "Diagnostika", "clipboard"),
    ("topshiriqlar", "Topshiriqlar va baholash", "flask"),
    ("rivojlanish", "Rivojlanish sozlamalari", "trophy"),
    ("foydalanuvchilar", "Foydalanuvchilar", "users"),
    ("malumotlar", "Foydalanuvchi ma'lumotlari", "chart"),
    ("tizim", "Tadqiqot va tizim", "shield"),
]

REGISTRY: dict[str, ModelConfig] = {}


def register(config):
    REGISTRY[config.key] = config
    return config


def get_config(key):
    return REGISTRY.get(key)


def grouped():
    """Hub sahifasi uchun: [(guruh_kodi, nomi, ikonka, [config, ...])]."""
    out = []
    for code, name, icon in GROUPS:
        items = [c for c in REGISTRY.values() if c.group == code]
        if items:
            out.append((code, name, icon, items))
    return out


def _build():
    from assignments.models import (
        AssignedTask, Assignment, CompetencyCheck, CompetencyItem, Criterion, Rubric,
        Score, Submission, SubmissionFile,
    )
    from content.models import Lesson, LessonProgress, Material, Section, Topic
    from core.enums import Component, Module
    from development.models import PlotResource, Simulation
    from diagnostics.models import (
        Answer, Attempt, Choice, Measurement, Question, Questionnaire, Recommendation,
        ScoringWeights,
    )
    from gamification.models import Badge, BadgeRule, UserBadge
    from goals.models import Goal, GoalTask
    from notifications.models import Notification, NotificationSetting
    from progress.models import ActivityLog, ComponentScore, DailyTask, ProgressSnapshot, Streak
    from reflection.models import ReflectionEntry, ReflectionPrompt
    from research.models import ExportJob, StatSummary

    from .forms_manage import UserManageForm
    from .models import AuditLog, EmailVerification

    # ------------------------------------------------------------ kontent
    register(ModelConfig(
        key="sections", builder_kind="fan", model=Section, group="kontent", icon="book",
        fields=["title", "description", "icon", "is_active"],
        columns=[("Fan", "title"), ("Slug", "slug"), ("Tartib", "order"), ("Faol", "is_active")],
        search=["title", "slug"], slug_from="title",
        children=[("Mavzular", "topics", "section")],
    ))
    register(ModelConfig(
        key="topics", builder_kind="mavzu", model=Topic, group="kontent", icon="book",
        fields=["section", "title", "summary", "component", "is_active"],
        columns=[("Mavzu", "title"), ("Fan", "section"), ("Komponent", "get_component_display"),
                 ("Tartib", "order"), ("Faol", "is_active")],
        search=["title", "slug", "section__title"], filters=["section"], slug_from="title",
        select_related=["section"], children=[("Darslar", "lessons", "topic")],
    ))
    register(ModelConfig(
        key="lessons", builder_kind="dars", model=Lesson, group="kontent", icon="book",
        fields=["topic", "title", "body", "video_url", "duration_minutes",
                "pass_threshold", "quiz", "is_active"],
        columns=[("Dars", "title"), ("Mavzu", "topic"), ("Daq.", "duration_minutes"),
                 ("Test", "quiz"), ("Faol", "is_active")],
        search=["title", "slug", "topic__title"], filters=["topic"], slug_from="title",
        select_related=["topic", "quiz"], children=[("Materiallar", "materials", "lesson")],
    ))
    register(ModelConfig(
        key="materials", model=Material, group="kontent", icon="book",
        fields=["lesson", "kind", "title", "body", "url", "file"],
        columns=[("Material", "title"), ("Turi", "get_kind_display"), ("Dars", "lesson"), ("Tartib", "order")],
        search=["title", "lesson__title"], filters=["lesson"], select_related=["lesson"],
    ))

    # ------------------------------------------- 3-blok: o'z-o'zini rivojlantirish
    # Menyudagi to'rt band. Keyslar va amaliy topshiriqlar — Assignment'ning bo'laklari:
    # modul/turi yashirin yoki cheklangan, shunda yozuv kerakli sahifada chiqadi.
    register(ModelConfig(
        key="visual_cases", site_url="assignments:cases", model=Assignment, group="rivojlantirish", icon="image",
        title="Muammoli vizual keyslar", singular_label="vizual keys",
        base_filter={"module": Module.VISUAL},
        defaults={"module": Module.VISUAL, "kind": Assignment.Kind.VISUAL},
        initial=lambda filters: {
            "component": Component.COG,
            "rubric": Rubric.objects.filter(slug="vizual-tahlil").values_list("pk", flat=True).first(),
        },
        fields=["title", "section", "image", "image_alt", "context_note", "body", "reference_solution",
                "component", "bloom_level", "rubric", "estimated_minutes", "difficulty", "allow_files",
                "is_active"],
        columns=[("Keys", "title"), ("Fan", "section"), ("Tasvir", "picture_url"),
                 ("Murak.", "difficulty"), ("Faol", "is_active")],
        search=["title", "slug", "body"], filters=["section"], slug_from="title",
        select_related=["section", "rubric"], children=[("Ishlar", "submissions", "assignment")],
        note="«Muammoli vizual keyslar» sahifasidagi keyslar. Tasvir yuklang (namunalarda tayyor tasvir bor — "
             "yangi rasm yuklansa, u ustun turadi). «Etalon yechim» ish yuborilgandan keyin ochiladi.",
    ))
    practice_modules = [Module.LAB, Module.TEACHER, Module.DIGITAL, Module.CREATIVE]
    practice_kinds = {Module.LAB: Assignment.Kind.LAB4, Module.TEACHER: Assignment.Kind.CASE,
                      Module.DIGITAL: Assignment.Kind.DIGITAL, Module.CREATIVE: Assignment.Kind.CREATIVE}
    register(ModelConfig(
        key="practice_tasks", site_url="assignments:module", model=Assignment, group="rivojlantirish", icon="microscope",
        title="Virtual laboratoriya va amaliy topshiriqlar", singular_label="amaliy topshiriq",
        base_filter={"module__in": practice_modules},
        initial=lambda filters: {
            "kind": practice_kinds.get(filters.get("module"), Assignment.Kind.LAB4),
            "component": Component.ACT,
        },
        limit_choices={"module": practice_modules, "kind": list(practice_kinds.values()) + [Assignment.Kind.LESSON_PLAN]},
        fields=["module", "kind", "title", "section", "body", "context_note", "image", "image_alt",
                "reference_solution", "component", "bloom_level", "rubric", "estimated_minutes", "difficulty",
                "allow_files", "is_active"],
        columns=[("Topshiriq", "title"), ("Bo'lim", "get_module_display"), ("Turi", "get_kind_display"),
                 ("Murak.", "difficulty"), ("Faol", "is_active")],
        search=["title", "slug", "body"], filters=["module"], slug_from="title",
        select_related=["rubric"], children=[("Ishlar", "submissions", "assignment")],
        note="«Virtual laboratoriya va amaliy topshiriqlar» sahifasining to'rt yorlig'i: Laboratoriya "
             "(4 bosqichli), Men — o'qituvchi (keys, dars loyihasi), Raqamli biologiya, Kreativ o'qituvchi.",
    ))
    register(ModelConfig(
        key="simulations", site_url="development:simulations", model=Simulation, group="rivojlantirish", icon="box",
        fields=["title", "section", "image", "image_alt", "url", "summary", "body", "parts", "task", "is_active"],
        columns=[("Simulyatsiya", "title"), ("Fan", "section"), ("Tasvir", "picture_url"),
                 ("Tartib", "order"), ("Faol", "is_active")],
        search=["title", "summary"], filters=["section"], slug_from="title", select_related=["section"],
        note="3D simulyatsiya — modelning 3D tasviri (render yoki skrinshot), qismlari va kuzatish topshirig'i. "
             "Havola berilsa, sahifada «Interaktiv 3D modelni ochish» tugmasi paydo bo'ladi.",
    ))
    register(ModelConfig(
        key="plot_resources", site_url="development:plot", model=PlotResource, group="rivojlantirish", icon="sprout",
        fields=["title", "kind", "season", "grade", "duration", "summary", "body", "image", "file", "url",
                "is_active"],
        columns=[("Resurs", "title"), ("Turi", "get_kind_display"), ("Mavsum", "get_season_display"),
                 ("Sinf", "grade"), ("Tartib", "order"), ("Faol", "is_active")],
        search=["title", "summary", "body"], filters=["kind", "season"], slug_from="title",
    ))

    # -------------------------------------------------------- diagnostika
    # Questionnaire bitta model, ammo boshqaruvda ikkita bo'lim: variantli testlar
    # (bilim testi + dars mustahkamlash testi) va Likert anketalar. Ular kesishmaydi
    # va birgalikda barcha so'rovnomalarni qamrab oladi.
    questionnaire_fields = ["title", "kind", "cut", "description", "instruction",
                            "question_count", "time_limit_minutes", "shuffle_questions",
                            "is_active"]
    register(ModelConfig(
        key="tests", builder_kind="test", builder_query="?kind=TEST",
        model=Questionnaire, group="diagnostika", icon="clipboard",
        title="Testlar", singular_label="test",
        base_filter={"kind__in": Questionnaire.TEST_KINDS},
        fields=questionnaire_fields,
        columns=[("Test", "title"), ("Turi", "get_kind_display"), ("Kesim", "get_cut_display"),
                 ("Savollar", "questions.count"), ("Faol", "is_active")],
        search=["title", "slug"], filters=["kind", "cut"], slug_from="title",
        children=[("Savollar", "questions", "questionnaire")],
        note="Variantli testlar: bilim testi (kesim diagnostikasi) va dars mustahkamlash testi. "
             "Likert anketalar alohida — \"Anketalar\" bo'limida.",
    ))
    register(ModelConfig(
        key="questionnaires", builder_kind="test", builder_query="?kind=LIKERT",
        model=Questionnaire, group="diagnostika", icon="clipboard",
        title="Anketalar (Likert)", singular_label="anketa",
        base_exclude={"kind__in": Questionnaire.TEST_KINDS},
        fields=questionnaire_fields,
        columns=[("Anketa", "title"), ("Turi", "get_kind_display"), ("Kesim", "get_cut_display"),
                 ("Savollar", "questions.count"), ("Faol", "is_active")],
        search=["title", "slug"], filters=["cut"], slug_from="title",
        children=[("Savollar", "questions", "questionnaire")],
        note="O'z-o'zini baholash anketalari (Likert shkalasi). Testlar — \"Testlar\" bo'limida.",
    ))
    register(ModelConfig(
        key="questions", model=Question, group="diagnostika", icon="clipboard",
        fields=["questionnaire", "text", "component", "bloom_level", "reverse_scored",
                "explanation", "is_active"],
        columns=[("Savol", "text"), ("So'rovnoma", "questionnaire"), ("Komp.", "component"),
                 ("Bloom", "bloom_level"), ("Tartib", "order"), ("Faol", "is_active")],
        search=["text", "questionnaire__title"],
        filters=["questionnaire", "questionnaire__kind", "component", "bloom_level"],
        select_related=["questionnaire"], children=[("Variantlar", "choices", "question")],
    ))
    register(ModelConfig(
        key="choices", model=Choice, group="diagnostika", icon="clipboard",
        fields=["question", "text", "is_correct"],
        columns=[("Variant", "text"), ("Savol", "question"), ("To'g'ri", "is_correct"), ("Tartib", "order")],
        search=["text", "question__text"], filters=["question"], select_related=["question"],
    ))
    register(ModelConfig(
        key="weights", model=ScoringWeights, group="diagnostika", icon="chart",
        fields=["name", "mot", "cog", "act", "ref", "cre", "is_active"],
        columns=[("Profil", "name"), ("MOT", "mot"), ("COG", "cog"), ("ACT", "act"),
                 ("REF", "ref"), ("CRE", "cre"), ("Faol", "is_active")],
        search=["name"],
        note="Faol profil bitta bo'ladi: yangisini faol qilsangiz, eskisi avtomatik arxivlanadi. "
             "Yig'indi 1.0 ga normallashtiriladi.",
    ))
    register(ModelConfig(
        key="recommendations", model=Recommendation, group="diagnostika", icon="spark",
        fields=["user", "measurement", "component", "title", "body", "is_active"],
        columns=[("Tavsiya", "title"), ("Foydalanuvchi", "user"), ("Komp.", "component"), ("Faol", "is_active")],
        search=["title", "user__email"], filters=["user"], select_related=["user"],
    ))

    # ------------------------------------------------------- topshiriqlar
    register(ModelConfig(
        key="rubrics", builder_kind="rubrika", model=Rubric, group="topshiriqlar", icon="check",
        fields=["title", "description", "is_active"],
        columns=[("Rubrika", "title"), ("Slug", "slug"), ("Faol", "is_active")],
        search=["title", "slug"], slug_from="title",
        children=[("Mezonlar", "criteria", "rubric"), ("Topshiriqlar", "assignments", "rubric")],
    ))
    register(ModelConfig(
        key="criteria", model=Criterion, group="topshiriqlar", icon="check",
        fields=["rubric", "name", "hint", "weight", "max_score", "level_descriptions"],
        columns=[("Mezon", "name"), ("Rubrika", "rubric"), ("Vazn", "weight"),
                 ("Maks.", "max_score"), ("Tartib", "order")],
        search=["name", "rubric__title"], filters=["rubric"], select_related=["rubric"],
    ))
    register(ModelConfig(
        key="assignments", model=Assignment, group="topshiriqlar", icon="flask",
        fields=["module", "kind", "section", "title", "image", "image_alt", "body", "context_note",
                "component", "bloom_level", "rubric", "reference_solution", "estimated_minutes",
                "allow_files", "difficulty", "is_active"],
        columns=[("Topshiriq", "title"), ("Modul", "get_module_display"), ("Turi", "get_kind_display"),
                 ("Komp.", "component"), ("Murak.", "difficulty"), ("Faol", "is_active")],
        search=["title", "slug", "body"], filters=["rubric", "module"], slug_from="title",
        select_related=["rubric"], children=[("Ishlar", "submissions", "assignment")],
    ))
    register(ModelConfig(
        key="assigned_tasks", model=AssignedTask, group="topshiriqlar", icon="send",
        fields=["assignment", "assigned_by", "deadline", "note"],
        columns=[("Topshiriq", "assignment"), ("Muddat", "deadline"), ("Kim", "assigned_by")],
        search=["assignment__title"], select_related=["assignment", "assigned_by"],
    ))
    register(ModelConfig(
        key="competency_items", model=CompetencyItem, group="topshiriqlar", icon="check",
        fields=["title", "description", "component", "is_active"],
        columns=[("Band", "title"), ("Komp.", "component"), ("Tartib", "order"), ("Faol", "is_active")],
        search=["title"],
    ))

    # -------------------------------------------------------- rivojlanish
    register(ModelConfig(
        key="reflection_prompts", model=ReflectionPrompt, group="rivojlanish", icon="pen",
        fields=["slot", "text", "hint", "is_active"],
        columns=[("O'rin", "get_slot_display"), ("Savol", "text"), ("Faol", "is_active")],
        search=["text"],
    ))
    register(ModelConfig(
        key="badges", builder_kind="nishon", model=Badge, group="rivojlanish", icon="trophy",
        fields=["code", "title", "emoji", "description", "how_to_earn", "is_active"],
        columns=[("Nishon", "__str__"), ("Kod", "code"), ("Tartib", "order"), ("Faol", "is_active")],
        search=["title", "code"], children=[("Qoidalar", "badge_rules", "badge")],
    ))
    register(ModelConfig(
        key="badge_rules", model=BadgeRule, group="rivojlanish", icon="trophy",
        fields=["badge", "metric", "threshold", "is_active"],
        columns=[("Nishon", "badge"), ("Metrika", "get_metric_display"), ("Chegara", "threshold"),
                 ("Faol", "is_active")],
        search=["badge__title"], filters=["badge"], select_related=["badge"],
    ))

    # ---------------------------------------------------- foydalanuvchilar
    register(ModelConfig(
        key="users", model=User, group="foydalanuvchilar", icon="users", title="Foydalanuvchilar",
        form_class=UserManageForm,
        columns=[("Email", "email"), ("Ism", "get_full_name"), ("Rollar", "profile.roles"), ("Faol", "profile.get_role_display"),
                 ("Bo'linma", "profile.get_study_arm_display"), ("Faol", "is_active"), ("Qo'shilgan", "date_joined")],
        search=["email", "first_name", "last_name"], filters=["profile__role", "profile__roles__contains", "is_active"],
        ordering=["-date_joined"], select_related=["profile"],
        children=[("Ishlar", "submissions", "student"), ("O'lchovlar", "measurements", "user"),
                  ("Maqsadlar", "goals", "user"), ("Refleksiyalar", "reflections", "user")],
        note="Rolni shu yerda o'zgartirasiz. Parol maydoni to'ldirilsa — yangi parol o'rnatiladi.",
    ))
    register(ModelConfig(
        key="email_verifications", model=EmailVerification, group="foydalanuvchilar", icon="send",
        fields=["user", "used_at"], can_add=False,
        columns=[("Foydalanuvchi", "user"), ("Token", "token"), ("Ishlatilgan", "used_at"),
                 ("Yaratilgan", "created_at")],
        search=["user__email"], filters=["user"], ordering=["-created_at"], select_related=["user"],
    ))

    # ------------------------------------------------ foydalanuvchi ma'lumoti
    register(ModelConfig(
        key="attempts", model=Attempt, group="malumotlar", icon="clipboard",
        fields=["user", "questionnaire", "cut", "status", "started_at", "finished_at"],
        columns=[("Foydalanuvchi", "user"), ("So'rovnoma", "questionnaire"), ("Kesim", "get_cut_display"),
                 ("Holat", "get_status_display"), ("Boshlangan", "started_at")],
        search=["user__email", "questionnaire__title"], filters=["user", "questionnaire", "status"],
        select_related=["user", "questionnaire"], children=[("Javoblar", "answers", "attempt")],
    ))
    register(ModelConfig(
        key="answers", model=Answer, group="malumotlar", icon="clipboard",
        fields=["attempt", "question", "choice", "value", "text_answer"],
        columns=[("Urinish", "attempt"), ("Savol", "question"), ("Variant", "choice"), ("Likert", "value")],
        search=["question__text", "attempt__user__email"], filters=["attempt"],
        select_related=["attempt__user", "question", "choice"], ordering=["-id"],
    ))
    register(ModelConfig(
        key="measurements", model=Measurement, group="malumotlar", icon="chart",
        fields=["user", "cut", "mot", "cog", "act", "ref", "cre", "source"],
        columns=[("Foydalanuvchi", "user"), ("Kesim", "get_cut_display"), ("SDI", "sdi"),
                 ("Manba", "source"), ("Bekor", "is_void"), ("Sana", "created_at")],
        search=["user__email"], filters=["user", "cut"], select_related=["user"],
        ordering=["-created_at"], can_edit=False, delete_mode="void",
        note="O'lchov muzlatilgan (TZ 6.3): tahrirlanmaydi. Xato bo'lsa — bekor qilinadi (void) "
             "va yangisi yaratiladi. SDI faol vaznlar bo'yicha avtomatik hisoblanadi.",
    ))
    register(ModelConfig(
        key="submissions", model=Submission, group="malumotlar", icon="flask",
        fields=["assignment", "student", "status", "payload", "self_percent", "mentor_percent",
                "mentor_feedback", "is_public", "reopen_allowed"],
        columns=[("Muallif", "student"), ("Topshiriq", "assignment"), ("Holat", "get_status_display"),
                 ("O'z", "self_percent"), ("Baho", "mentor_percent"), ("Yuborilgan", "submitted_at")],
        search=["student__email", "assignment__title"], filters=["student", "assignment", "status"],
        select_related=["student", "assignment"],
        children=[("Baholar", "scores", "submission"), ("Fayllar", "submission_files", "submission")],
    ))
    register(ModelConfig(
        key="submission_files", model=SubmissionFile, group="malumotlar", icon="download",
        fields=["submission", "file", "original_name"],
        columns=[("Fayl", "__str__"), ("Ish", "submission"), ("Hajm", "size"), ("Sana", "created_at")],
        search=["original_name", "submission__student__email"], filters=["submission"],
        select_related=["submission__student"], ordering=["-created_at"],
    ))
    register(ModelConfig(
        key="scores", model=Score, group="malumotlar", icon="check",
        fields=["submission", "criterion", "scorer", "value", "comment", "author"],
        columns=[("Ish", "submission"), ("Mezon", "criterion"), ("Kim", "get_scorer_display"), ("Ball", "value")],
        search=["submission__student__email", "criterion__name"], filters=["submission"],
        select_related=["submission__student", "criterion"], ordering=["-id"],
    ))
    register(ModelConfig(
        key="competency_checks", model=CompetencyCheck, group="malumotlar", icon="check",
        fields=["user", "item", "level", "evidence"],
        columns=[("Foydalanuvchi", "user"), ("Band", "item"), ("Daraja", "get_level_display")],
        search=["user__email", "item__title"], filters=["user", "item"], select_related=["user", "item"],
    ))
    register(ModelConfig(
        key="goals", model=Goal, group="malumotlar", icon="target",
        fields=["user", "title", "component", "why", "resources", "expected_result", "start_date",
                "deadline", "status", "mentor_comment", "mentor_approved"],
        columns=[("Maqsad", "title"), ("Foydalanuvchi", "user"), ("Holat", "get_status_display"),
                 ("Muddat", "deadline"), ("Tasdiq", "mentor_approved")],
        search=["title", "user__email"], filters=["user", "status"], select_related=["user"],
        children=[("Vazifalar", "goal_tasks", "goal")],
    ))
    register(ModelConfig(
        key="goal_tasks", model=GoalTask, group="malumotlar", icon="target",
        fields=["goal", "title", "week", "is_done"],
        columns=[("Vazifa", "title"), ("Maqsad", "goal"), ("Hafta", "week"), ("Bajarildi", "is_done")],
        search=["title", "goal__title"], filters=["goal"], select_related=["goal"],
    ))
    register(ModelConfig(
        key="reflections", model=ReflectionEntry, group="malumotlar", icon="pen",
        fields=["user", "kind", "submission", "goal", "q1", "q2", "q3", "q4", "free_text", "tags",
                "quality_score", "mentor_comment"],
        columns=[("Foydalanuvchi", "user"), ("Turi", "get_kind_display"), ("Matn", "preview"),
                 ("Sifat", "quality_score"), ("Sana", "created_at")],
        search=["user__email", "q1", "free_text", "tags"], filters=["user", "kind"],
        select_related=["user"],
    ))
    register(ModelConfig(
        key="lesson_progress", model=LessonProgress, group="malumotlar", icon="book",
        fields=["user", "lesson", "status", "score", "attempts", "completed_at"],
        columns=[("Foydalanuvchi", "user"), ("Dars", "lesson"), ("Holat", "get_status_display"),
                 ("Ball", "score"), ("Urinish", "attempts")],
        search=["user__email", "lesson__title"], filters=["user", "lesson"],
        select_related=["user", "lesson"], ordering=["-updated_at"],
    ))
    register(ModelConfig(
        key="component_scores", model=ComponentScore, group="malumotlar", icon="chart",
        fields=["user", "component", "value", "diagnostic_part", "practice_part", "sample_size"],
        columns=[("Foydalanuvchi", "user"), ("Komp.", "component"), ("Ball", "value"),
                 ("Hisoblangan", "computed_at")],
        search=["user__email"], filters=["user", "component"], select_related=["user"],
        ordering=["user", "component"],
    ))
    register(ModelConfig(
        key="snapshots", model=ProgressSnapshot, group="malumotlar", icon="chart",
        fields=["user", "date", "mot", "cog", "act", "ref", "cre", "sdi"],
        columns=[("Foydalanuvchi", "user"), ("Sana", "date"), ("SDI", "sdi")],
        search=["user__email"], filters=["user"], select_related=["user"], ordering=["-date"],
    ))
    register(ModelConfig(
        key="activity_log", model=ActivityLog, group="malumotlar", icon="calendar",
        fields=["user", "action", "object_ref", "points", "meta"],
        columns=[("Foydalanuvchi", "user"), ("Harakat", "get_action_display"), ("Obyekt", "object_ref"),
                 ("Ball", "points"), ("Sana", "created_at")],
        search=["user__email", "object_ref"], filters=["user", "action"], select_related=["user"],
    ))
    register(ModelConfig(
        key="streaks", model=Streak, group="malumotlar", icon="flame",
        fields=["user", "current", "longest", "last_active_date", "total_active_days"],
        columns=[("Foydalanuvchi", "user"), ("Joriy", "current"), ("Eng uzun", "longest"),
                 ("Oxirgi", "last_active_date"), ("Jami", "total_active_days")],
        search=["user__email"], filters=["user"], select_related=["user"],
    ))
    register(ModelConfig(
        key="daily_tasks", model=DailyTask, group="malumotlar", icon="calendar",
        fields=["user", "date", "title", "description", "component", "done", "note"],
        columns=[("Sana", "date"), ("Foydalanuvchi", "user"), ("Topshiriq", "title"),
                 ("Komp.", "component"), ("Bajarildi", "done")],
        search=["title", "user__email"], filters=["user"], select_related=["user"],
    ))
    register(ModelConfig(
        key="user_badges", model=UserBadge, group="malumotlar", icon="trophy",
        fields=["user", "badge", "reason"],
        columns=[("Foydalanuvchi", "user"), ("Nishon", "badge"), ("Sabab", "reason"), ("Sana", "created_at")],
        search=["user__email", "badge__title"], filters=["user", "badge"], select_related=["user", "badge"],
    ))
    register(ModelConfig(
        key="notifications", model=Notification, group="malumotlar", icon="bell",
        fields=["user", "kind", "title", "body", "url", "read_at"],
        columns=[("Foydalanuvchi", "user"), ("Turi", "get_kind_display"), ("Sarlavha", "title"),
                 ("O'qilgan", "read_at"), ("Sana", "created_at")],
        search=["title", "user__email"], filters=["user", "kind"], select_related=["user"],
    ))
    register(ModelConfig(
        key="notification_settings", model=NotificationSetting, group="malumotlar", icon="bell",
        fields=["user", "email_graded", "email_deadline", "email_new_assignment", "email_weekly", "email_badge"],
        columns=[("Foydalanuvchi", "user"), ("Baho", "email_graded"), ("Muddat", "email_deadline"),
                 ("Topshiriq", "email_new_assignment"), ("Haftalik", "email_weekly"), ("Nishon", "email_badge")],
        search=["user__email"], filters=["user"], select_related=["user"],
    ))

    # -------------------------------------------------------------- tizim
    register(ModelConfig(
        key="exports", model=ExportJob, group="tizim", icon="download",
        fields=["requested_by", "fmt", "cuts", "arms", "row_count", "filename"], can_add=False,
        columns=[("Sana", "created_at"), ("Kim", "requested_by"), ("Format", "fmt"),
                 ("Qatorlar", "row_count"), ("Fayl", "filename")],
        search=["filename", "requested_by__email"], select_related=["requested_by"],
    ))
    register(ModelConfig(
        key="stat_summaries", model=StatSummary, group="tizim", icon="chart",
        fields=["cut", "arm", "component", "n", "mean", "sd", "minimum", "maximum"],
        columns=[("Kesim", "get_cut_display"), ("Bo'linma", "get_arm_display"), ("Ko'rsatkich", "component"),
                 ("n", "n"), ("O'rtacha", "mean"), ("SD", "sd")],
        search=["component"], filters=["cut", "arm"], ordering=["cut", "arm", "component"],
    ))
    register(ModelConfig(
        key="audit_log", model=AuditLog, group="tizim", icon="shield",
        can_add=False, can_edit=False, can_delete=False,
        columns=[("Vaqt", "created_at"), ("Kim", "actor"), ("Harakat", "action"),
                 ("Obyekt", "target"), ("IP", "ip")],
        search=["action", "target", "actor__email"], filters=["actor", "action"], select_related=["actor"],
        note="Audit jurnali faqat o'qish uchun (NFR-14).",
    ))


_build()
