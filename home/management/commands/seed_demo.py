"""
Platformani ishga tayyorlash: kontent, savollar, topshiriqlar, rubrikalar, nishonlar.

    python manage.py seed_demo                # faqat kontent (idempotent)
    python manage.py seed_demo --with-users   # + demo foydalanuvchilar va o'lchovlar
    python manage.py seed_demo --reset        # avval kontentni tozalab, qaytadan yuklaydi

Kontent `*/seed_data.py` fayllaridan olinadi — uni tahrirlash uchun kod bilishning
hojati yo'q, matnlarni to'g'ridan-to'g'ri o'zgartirsangiz kifoya.
"""

import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from assignments.models import Assignment, CompetencyItem, Criterion, Rubric
from assignments.seed_data import (
    ASSIGNMENTS,
    BADGES,
    COMPETENCY_ITEMS,
    REFLECTION_PROMPTS,
    RUBRICS,
)
from content.models import Lesson, Material, Section, Topic
from content.seed_data import SECTIONS
from core.enums import BloomLevel, Component, Cut, Role, StudyArm
from diagnostics.models import Choice, Question, Questionnaire, ScoringWeights
from diagnostics.seed_data import LESSON_QUIZZES, LIKERT_ITEMS, TEST_ITEMS
from gamification.models import Badge, BadgeRule
from reflection.models import ReflectionPrompt


class Command(BaseCommand):
    help = "BioTeacher platformasini boshlang'ich kontent bilan to'ldiradi."

    def add_arguments(self, parser):
        parser.add_argument("--with-users", action="store_true",
                            help="Demo mentor va talabalarni ham yaratadi.")
        parser.add_argument("--reset", action="store_true",
                            help="Mavjud kontentni o'chirib, qaytadan yuklaydi.")
        parser.add_argument("--students", type=int, default=24,
                            help="--with-users bilan yaratiladigan talabalar soni.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._reset()

        self.stdout.write(self.style.MIGRATE_HEADING("BioTeacher — boshlang'ich kontent"))
        self._weights()
        self._reflection_prompts()
        rubrics = self._rubrics()
        self._assignments(rubrics)
        self._competency()
        self._badges()
        quizzes = self._lesson_quizzes()
        self._content(quizzes)
        self._diagnostics()

        if options["with_users"]:
            self._demo_users(options["students"])

        self.stdout.write(self.style.SUCCESS("\nTayyor. Endi /hisob/royxat/ orqali ro'yxatdan o'ting."))

    # ------------------------------------------------------------------ reset

    def _reset(self):
        self.stdout.write(self.style.WARNING("Kontent tozalanmoqda…"))
        from assignments.models import Submission

        Submission.all_objects.all().hard_delete()
        Assignment.all_objects.all().hard_delete()
        Criterion.objects.all().delete()
        Rubric.all_objects.all().hard_delete()
        Material.objects.all().delete()
        Lesson.all_objects.all().hard_delete()
        Topic.all_objects.all().hard_delete()
        Section.all_objects.all().hard_delete()
        Choice.objects.all().delete()
        Question.all_objects.all().hard_delete()
        Questionnaire.all_objects.all().hard_delete()
        CompetencyItem.all_objects.all().hard_delete()
        BadgeRule.objects.all().delete()
        Badge.all_objects.all().hard_delete()
        ReflectionPrompt.objects.all().delete()

    # ------------------------------------------------------------------ steps

    def _weights(self):
        profile, created = ScoringWeights.objects.get_or_create(
            name="Standart", defaults={"is_active": True}
        )
        self.stdout.write(f"  Vaznlar profili: {'yaratildi' if created else 'mavjud'} — {profile.as_dict()}")

    def _reflection_prompts(self):
        for slot, text, hint in REFLECTION_PROMPTS:
            ReflectionPrompt.objects.get_or_create(
                slot=slot, text=text, defaults={"hint": hint, "is_active": True}
            )
        self.stdout.write(f"  Refleksiya savollari: {ReflectionPrompt.objects.count()} ta")

    def _rubrics(self):
        mapping = {}
        for data in RUBRICS:
            rubric, _ = Rubric.objects.update_or_create(
                slug=data["slug"],
                defaults={"title": data["title"], "description": data["description"]},
            )
            for order, criterion in enumerate(data["criteria"]):
                Criterion.objects.update_or_create(
                    rubric=rubric,
                    name=criterion["name"],
                    defaults={
                        "hint": criterion["hint"],
                        "weight": criterion["weight"],
                        "max_score": criterion["max_score"],
                        "level_descriptions": criterion["levels"],
                        "order": order,
                    },
                )
            mapping[data["slug"]] = rubric
        self.stdout.write(f"  Rubrikalar: {len(mapping)} ta")
        return mapping

    def _assignments(self, rubrics):
        for data in ASSIGNMENTS:
            Assignment.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "module": data["module"],
                    "kind": data["kind"],
                    "title": data["title"],
                    "body": data["body"],
                    "context_note": data.get("context", ""),
                    "component": data["component"],
                    "bloom_level": data["bloom"],
                    "rubric": rubrics[data["rubric"]],
                    "reference_solution": data.get("reference", ""),
                    "estimated_minutes": data["minutes"],
                    "difficulty": data["difficulty"],
                    "is_active": True,
                },
            )
        self.stdout.write(f"  Topshiriqlar: {Assignment.objects.count()} ta")

    def _competency(self):
        for order, (component, title, description) in enumerate(COMPETENCY_ITEMS):
            CompetencyItem.objects.update_or_create(
                title=title,
                defaults={"component": component, "description": description, "order": order},
            )
        self.stdout.write(f"  Kompetensiya bandlari: {CompetencyItem.objects.count()} ta")

    def _badges(self):
        for order, data in enumerate(BADGES):
            badge, _ = Badge.objects.update_or_create(
                code=data["code"],
                defaults={
                    "title": data["title"],
                    "emoji": data["emoji"],
                    "description": data["description"],
                    "how_to_earn": data["how"],
                    "order": order,
                },
            )
            badge.rules.all().delete()
            for metric, threshold in data["rules"]:
                BadgeRule.objects.create(badge=badge, metric=metric, threshold=threshold)
        self.stdout.write(f"  Nishonlar: {Badge.objects.count()} ta")

    def _lesson_quizzes(self):
        """Har bir mavzu uchun mustahkamlash testini yaratadi (FR-20)."""
        quizzes = {}
        for topic_slug, items in LESSON_QUIZZES.items():
            questionnaire, _ = Questionnaire.objects.update_or_create(
                slug=f"quiz-{topic_slug}",
                defaults={
                    "title": f"Mustahkamlash testi — {topic_slug.replace('-', ' ')}",
                    "kind": Questionnaire.Kind.TEST,
                    "cut": Cut.INITIAL,
                    "instruction": "Har bir savolga bitta to'g'ri javobni tanlang.",
                    "question_count": 0,
                    "shuffle_questions": True,
                },
            )
            questionnaire.questions.all().delete()
            for order, (text, choices, correct) in enumerate(items):
                question = Question.objects.create(
                    questionnaire=questionnaire,
                    text=text,
                    component=Component.COG,
                    bloom_level=BloomLevel.UNDERSTAND,
                    order=order,
                )
                for index, choice_text in enumerate(choices):
                    Choice.objects.create(
                        question=question, text=choice_text,
                        is_correct=(index == correct), order=index,
                    )
            quizzes[topic_slug] = questionnaire
        self.stdout.write(f"  Dars testlari: {len(quizzes)} ta")
        return quizzes

    def _content(self, quizzes):
        lesson_count = 0
        for section_order, section_data in enumerate(SECTIONS):
            section, _ = Section.objects.update_or_create(
                slug=section_data["slug"],
                defaults={
                    "title": section_data["title"],
                    "icon": section_data["icon"],
                    "description": section_data["description"],
                    "order": section_order,
                },
            )
            for topic_order, topic_data in enumerate(section_data["topics"]):
                topic, _ = Topic.objects.update_or_create(
                    section=section,
                    slug=topic_data["slug"],
                    defaults={
                        "title": topic_data["title"],
                        "summary": topic_data["summary"],
                        "component": topic_data["component"],
                        "order": topic_order,
                    },
                )
                for lesson_order, lesson_data in enumerate(topic_data["lessons"]):
                    lesson, _ = Lesson.objects.update_or_create(
                        topic=topic,
                        slug=lesson_data["slug"],
                        defaults={
                            "title": lesson_data["title"],
                            "body": lesson_data["body"],
                            "duration_minutes": lesson_data["duration"],
                            "quiz": quizzes.get(topic_data["slug"]),
                            "order": lesson_order,
                        },
                    )
                    lesson.materials.all().delete()
                    for material_order, material in enumerate(lesson_data.get("materials", [])):
                        Material.objects.create(
                            lesson=lesson,
                            kind=material["kind"],
                            title=material["title"],
                            body=material.get("body", ""),
                            url=material.get("url", ""),
                            order=material_order,
                        )
                    lesson_count += 1
        self.stdout.write(
            f"  Kontent: {Section.objects.count()} bo'lim, {Topic.objects.count()} mavzu, "
            f"{lesson_count} dars"
        )

    def _diagnostics(self):
        """FR-07, FR-08 — har bir kesim uchun anketa va bilim testi."""
        cut_labels = {
            Cut.INITIAL: "Boshlang'ich",
            Cut.INTERIM_1: "1-oraliq",
            Cut.INTERIM_2: "2-oraliq",
            Cut.FINAL: "Yakuniy",
        }
        for cut, label in cut_labels.items():
            # --- Likert anketa ---
            likert, _ = Questionnaire.objects.update_or_create(
                slug=f"anketa-{cut.lower()}",
                defaults={
                    "title": f"{label} diagnostika: o'z-o'zini baholash anketasi",
                    "kind": Questionnaire.Kind.LIKERT,
                    "cut": cut,
                    "description": "5 komponent bo'yicha o'z-o'zini baholash. To'g'ri yoki noto'g'ri "
                                   "javob yo'q — halol javob bering, natija faqat sizga ko'rinadi.",
                    "instruction": "Har bir gap sizga qanchalik mos kelishini belgilang:\n"
                                   "1 — hech qachon, 2 — kamdan-kam, 3 — ba'zan, 4 — ko'pincha, 5 — doimo.",
                    "question_count": 0,
                    "shuffle_questions": True,
                },
            )
            likert.questions.all().delete()
            for order, (component, text, reverse) in enumerate(LIKERT_ITEMS):
                Question.objects.create(
                    questionnaire=likert, text=text, component=component,
                    bloom_level=BloomLevel.KNOW, reverse_scored=reverse, order=order,
                )

            # --- Bilim testi ---
            test, _ = Questionnaire.objects.update_or_create(
                slug=f"test-{cut.lower()}",
                defaults={
                    "title": f"{label} diagnostika: kasbiy bilim testi",
                    "kind": Questionnaire.Kind.TEST,
                    "cut": cut,
                    "description": "Biologiya va o'qitish metodikasi bo'yicha Bloom darajalariga "
                                   "taqsimlangan savollar.",
                    "instruction": "Har bir savolga bitta eng to'g'ri javobni tanlang. "
                                   "Javoblar avtomatik saqlanadi.",
                    "question_count": 20,
                    "time_limit_minutes": 30,
                    "shuffle_questions": True,
                },
            )
            test.questions.all().delete()
            for order, item in enumerate(TEST_ITEMS):
                component, bloom, text, choices, correct, explanation = item
                question = Question.objects.create(
                    questionnaire=test, text=text, component=component,
                    bloom_level=bloom, explanation=explanation, order=order,
                )
                for index, choice_text in enumerate(choices):
                    Choice.objects.create(
                        question=question, text=choice_text,
                        is_correct=(index == correct), order=index,
                    )

        self.stdout.write(
            f"  Diagnostika: {Questionnaire.objects.count()} so'rovnoma, "
            f"{Question.objects.count()} savol"
        )

    # ------------------------------------------------------- demo foydalanuvchilar

    def _demo_users(self, student_count):
        """
        Tajriba/nazorat guruhlari va real ko'rinishdagi o'lchovlar yaratadi —
        tadqiqot moduli va statistikani sinab ko'rish uchun.
        """
        from django.contrib.auth import get_user_model

        from accounts.models import Enrollment, Profile, StudyGroup
        from diagnostics.models import Measurement
        from progress.models import ComponentScore

        User = get_user_model()
        random.seed(20260907)  # takrorlanadigan demo ma'lumot

        mentor, created = User.objects.get_or_create(
            email="mentor@bioteacher.uz",
            defaults={"first_name": "Nodira", "last_name": "Karimova", "email_verified": True},
        )
        if created:
            mentor.set_password("bioteacher2026")
            mentor.save()
        mentor.profile.role = Role.TEACHER
        mentor.profile.otm = "Toshkent davlat pedagogika universiteti"
        mentor.profile.save()

        researcher, created = User.objects.get_or_create(
            email="tadqiqotchi@bioteacher.uz",
            defaults={"first_name": "Sanjar", "last_name": "Yo'ldoshev", "email_verified": True},
        )
        if created:
            researcher.set_password("bioteacher2026")
            researcher.save()
        researcher.profile.role = Role.RESEARCHER
        researcher.profile.save()

        groups = {}
        for arm, name in [(StudyArm.EXPERIMENTAL, "BIO-21 (tajriba)"),
                          (StudyArm.CONTROL, "BIO-22 (nazorat)")]:
            group, _ = StudyGroup.objects.get_or_create(
                name=name,
                defaults={
                    "otm": "Toshkent davlat pedagogika universiteti",
                    "faculty": "Tabiiy fanlar",
                    "course": 3,
                    "teacher": mentor,
                    "study_arm": arm,
                },
            )
            group.study_arm = arm
            group.teacher = mentor
            group.save()
            groups[arm] = group

        first_names = ["Aziza", "Bekzod", "Dilnoza", "Eldor", "Feruza", "G'olib", "Hulkar",
                       "Islom", "Jasmina", "Kamola", "Lola", "Muhammad", "Nilufar", "Otabek",
                       "Parvina", "Qodir", "Ruxshona", "Sardor", "Tohir", "Umida",
                       "Vazira", "Xurshid", "Yulduz", "Zafar"]
        last_names = ["Abdullayev", "Bekmurodova", "Choriyev", "Do'stova", "Ergashev",
                      "Fayzullayeva", "G'aniyev", "Hamidova", "Ibragimov", "Jo'rayeva",
                      "Karimov", "Latipova", "Mahmudov", "Nazarova", "Oripov", "Po'latova",
                      "Qosimov", "Rahimova", "Saidov", "To'rayeva", "Usmonov", "Valiyeva",
                      "Xolmatov", "Yusupova"]

        created_students = 0
        for index in range(student_count):
            arm = StudyArm.EXPERIMENTAL if index % 2 == 0 else StudyArm.CONTROL
            group = groups[arm]
            email = f"talaba{index + 1}@bioteacher.uz"
            student, is_new = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_names[index % len(first_names)],
                    "last_name": last_names[index % len(last_names)],
                    "email_verified": True,
                },
            )
            if is_new:
                student.set_password("bioteacher2026")
                student.save()
                created_students += 1

            profile = student.profile
            profile.role = Role.STUDENT
            profile.group = group
            profile.otm = group.otm
            profile.faculty = group.faculty
            profile.course = group.course
            profile.research_consent = True
            profile.research_consent_at = timezone.now()
            profile.onboarding_done = True
            profile.save()
            Enrollment.objects.get_or_create(student=student, group=group)

            self._simulate_measurements(student, arm, Measurement, ComponentScore)

        self.stdout.write(self.style.SUCCESS(
            f"\n  Demo foydalanuvchilar: {created_students} yangi talaba, "
            f"{StudyGroup.objects.count()} guruh"
        ))
        self.stdout.write("  Kirish ma'lumotlari (parol: bioteacher2026):")
        self.stdout.write("    mentor@bioteacher.uz        — o'qituvchi kabineti")
        self.stdout.write("    tadqiqotchi@bioteacher.uz   — tadqiqot paneli")
        self.stdout.write("    talaba1@bioteacher.uz …     — talaba kabineti")

    def _simulate_measurements(self, student, arm, Measurement, ComponentScore):
        """
        Boshlang'ich va yakuniy kesimlarni yaratadi.

        Tajriba guruhida o'sish kuchliroq — bu STATISTIKA MODULINI SINASH uchun
        modellashtirilgan demo ma'lumot, real tadqiqot natijasi emas.
        """
        if Measurement.objects.filter(user=student).exists():
            return

        base = {component: random.uniform(38, 62) for component in Component.values}
        gain = (14, 26) if arm == StudyArm.EXPERIMENTAL else (4, 12)

        initial = Measurement.objects.create(
            user=student, cut=Cut.INITIAL, source="seed",
            mot=round(base["MOT"], 2), cog=round(base["COG"], 2), act=round(base["ACT"], 2),
            ref=round(base["REF"], 2), cre=round(base["CRE"], 2),
        )
        initial.created_at = timezone.now() - timezone.timedelta(days=120)
        Measurement.objects.filter(pk=initial.pk).update(created_at=initial.created_at)

        final_values = {
            component: min(97.0, value + random.uniform(*gain))
            for component, value in base.items()
        }
        final = Measurement.objects.create(
            user=student, cut=Cut.FINAL, source="seed",
            mot=round(final_values["MOT"], 2), cog=round(final_values["COG"], 2),
            act=round(final_values["ACT"], 2), ref=round(final_values["REF"], 2),
            cre=round(final_values["CRE"], 2),
        )
        Measurement.objects.filter(pk=final.pk).update(
            created_at=timezone.now() - timezone.timedelta(days=2)
        )

        for component, value in final_values.items():
            ComponentScore.objects.update_or_create(
                user=student, component=component,
                defaults={"value": round(value, 2), "sample_size": 1},
            )
