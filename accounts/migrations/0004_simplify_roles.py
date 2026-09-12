"""Rollarni ikkitaga qisqartirish: TEACHER (o'rganuvchi) va ADMIN (CRUD)."""

from django.db import migrations, models

# Eski rol → yangi rol.
ROLE_MAP = {
    "STUDENT": "TEACHER",
    "TEACHER": "TEACHER",
    "METHODIST": "ADMIN",
    "RESEARCHER": "ADMIN",
    "ADMIN": "ADMIN",
}


def forwards(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    for old, new in ROLE_MAP.items():
        if old != new:
            Profile.objects.filter(role=old).update(role=new)
    # Ro'yxatda bo'lmagan qiymatlar ham o'rganuvchiga tushadi.
    Profile.objects.exclude(role__in=["TEACHER", "ADMIN"]).update(role="TEACHER")


def backwards(apps, schema_editor):
    """Eski rollarni tiklab bo'lmaydi — hammasi TEACHER bo'lib qoladi."""


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_enrollment_uniq_active_enrollment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('TEACHER', "O'qituvchi"), ('ADMIN', 'Administrator')], default='TEACHER', max_length=20, verbose_name='rol'),
        ),
        migrations.RunPython(forwards, backwards),
    ]
