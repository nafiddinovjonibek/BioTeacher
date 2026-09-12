"""
Muddat eslatmalari va haftalik xulosa (FR-15, FR-65).

Cron/Task Scheduler orqali kuniga bir marta chaqiriladi:

    python manage.py send_reminders                 # muddat eslatmalari
    python manage.py send_reminders --weekly        # + haftalik xulosa (dushanbada)
    python manage.py send_reminders --dry-run       # yubormasdan ko'rish

Windows Task Scheduler misoli (har kuni 08:00):
    schtasks /create /tn BioTeacherReminders /tr "D:\\...\\env\\Scripts\\python.exe
             D:\\...\\manage.py send_reminders --weekly" /sc daily /st 08:00
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from assignments.models import AssignedTask, Submission
from goals.models import Goal
from notifications.models import NotificationType
from notifications.services import notify
from progress.services import current_sdi, weakest_components

# Muddat shu kunlar qolganda eslatiladi.
REMIND_DAYS_BEFORE = 3


class Command(BaseCommand):
    help = "Muddat eslatmalari va haftalik rivojlanish xulosasini yuboradi."

    def add_arguments(self, parser):
        parser.add_argument("--weekly", action="store_true",
                            help="Haftalik xulosani ham yuboradi (dushanba kunlari).")
        parser.add_argument("--dry-run", action="store_true",
                            help="Hech narsa yubormaydi, faqat nimani yuborishini ko'rsatadi.")
        parser.add_argument("--force-weekly", action="store_true",
                            help="Haftalik xulosani kun kunligidan qat'i nazar yuboradi.")

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        if self.dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — hech narsa yuborilmaydi.\n"))

        sent = self._goal_deadlines()
        sent += self._assignment_deadlines()

        if options["weekly"] and (options["force_weekly"] or timezone.localdate().weekday() == 0):
            sent += self._weekly_digest()

        self.stdout.write(self.style.SUCCESS(f"\nJami: {sent} ta bildirishnoma."))

    def _send(self, user, kind, title, body, url=""):
        self.stdout.write(f"  → {user.email}: {title}")
        if not self.dry_run:
            notify(user, kind, title=title, body=body, url=url)
        return 1

    # ------------------------------------------------------------ maqsadlar

    def _goal_deadlines(self):
        """FR-15 — maqsad muddati yaqinlashganda eslatma."""
        today = timezone.localdate()
        limit = today + timezone.timedelta(days=REMIND_DAYS_BEFORE)
        goals = Goal.objects.filter(
            status=Goal.Status.ACTIVE, reminder_sent=False, deadline__lte=limit
        ).select_related("user")

        self.stdout.write(self.style.MIGRATE_HEADING("Maqsad muddatlari"))
        count = 0
        for goal in goals:
            days = (goal.deadline - today).days
            if days < 0:
                title = f"Maqsad muddati o'tdi: {goal.title}"
                body = (f"Muddat {goal.deadline:%d.%m.%Y} edi. Bajarilgan: "
                        f"{goal.progress_percent()}%. Maqsadni yakunlang yoki muddatini yangilang.")
            else:
                title = f"Maqsad muddati yaqin: {goal.title}"
                body = (f"{days} kun qoldi ({goal.deadline:%d.%m.%Y}). Bajarilgan: "
                        f"{goal.progress_percent()}%. Qolgan vazifalarni ko'rib chiqing.")

            count += self._send(
                goal.user, NotificationType.DEADLINE, title, body, f"/maqsadlar/{goal.pk}/"
            )
            if not self.dry_run:
                goal.reminder_sent = True
                goal.save(update_fields=["reminder_sent", "updated_at"])

        if count == 0:
            self.stdout.write("  (eslatma kerak bo'lgan maqsad yo'q)")
        return count

    # --------------------------------------------------------- topshiriqlar

    def _assignment_deadlines(self):
        """FR-15 — tayinlangan topshiriq muddati."""
        from accounts.services import learner_queryset

        now = timezone.now()
        limit = now + timezone.timedelta(days=REMIND_DAYS_BEFORE)
        assigned = AssignedTask.objects.filter(
            deadline__isnull=False, deadline__gte=now, deadline__lte=limit
        ).select_related("assignment")

        self.stdout.write(self.style.MIGRATE_HEADING("Topshiriq muddatlari"))
        count = 0
        students = list(learner_queryset())
        for task in assigned:
            done = set(
                Submission.objects.filter(
                    assignment=task.assignment,
                    status__in=[Submission.Status.SUBMITTED, Submission.Status.GRADED],
                ).values_list("student_id", flat=True)
            )
            for student in students:
                if student.pk in done:
                    continue
                count += self._send(
                    student,
                    NotificationType.DEADLINE,
                    f"Muddat yaqin: {task.assignment.title}",
                    f"Topshirish muddati — {task.deadline:%d.%m.%Y %H:%M}.",
                    f"/topshiriqlar/{task.assignment.slug}/",
                )

        if count == 0:
            self.stdout.write("  (muddati yaqin topshiriq yo'q)")
        return count

    # ------------------------------------------------------ haftalik xulosa

    def _weekly_digest(self):
        """FR-65 — haftalik rivojlanish xulosasi."""
        from accounts.services import learner_queryset
        from core.enums import Component, level_for
        from progress.models import ActivityLog

        week_ago = timezone.now() - timezone.timedelta(days=7)

        self.stdout.write(self.style.MIGRATE_HEADING("Haftalik xulosa"))
        count = 0
        students = learner_queryset().filter(profile__onboarding_done=True)

        for student in students:
            activities = ActivityLog.objects.filter(user=student, created_at__gte=week_ago)
            submissions = activities.filter(action=ActivityLog.Action.SUBMISSION).count()
            reflections = activities.filter(action=ActivityLog.Action.REFLECTION).count()
            sdi = current_sdi(student)

            if sdi is None:
                continue

            weak = weakest_components(student, limit=1)
            weak_label = Component(weak[0]).label if weak else "—"

            if activities.exists():
                body = (
                    f"Bu hafta: {submissions} ta topshiriq, {reflections} ta refleksiya.\n"
                    f"Joriy SDI: {sdi:.0f}% ({level_for(sdi)[1]} daraja).\n"
                    f"Eng ko'p e'tibor talab qiladigan yo'nalish: {weak_label}."
                )
            else:
                body = (
                    "Bu hafta platformada faoliyat qayd etilmadi.\n"
                    f"Joriy SDI: {sdi:.0f}%. Rivojlanish uzluksizlikni talab qiladi — "
                    "bugun 15 daqiqalik topshiriqdan boshlang."
                )

            count += self._send(
                student, NotificationType.WEEKLY, "Haftalik rivojlanish xulosasi",
                body, "/rivojlanish/",
            )

        if count == 0:
            self.stdout.write("  (xulosa yuboriladigan foydalanuvchi yo'q)")
        return count
