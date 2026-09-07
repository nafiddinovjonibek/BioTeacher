"""
Rolga asoslangan ruxsat dekoratorlari va obyekt darajasidagi tekshiruvlar (NFR-12).

Qoida FR-00: talaba boshqa talabaning natijasini hech qachon ko'rmaydi.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from core.enums import Role


def get_profile(user):
    return getattr(user, "profile", None)


def has_role(user, *roles):
    profile = get_profile(user)
    if profile is None:
        return False
    if user.is_superuser:
        return True
    return profile.role in {getattr(r, "value", r) for r in roles}


def role_required(*roles):
    """View'ni faqat berilgan rollarga ochadi."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not has_role(request.user, *roles):
                raise PermissionDenied("Bu bo'limga kirish huquqingiz yo'q.")
            return view(request, *args, **kwargs)

        return wrapper

    return decorator


student_required = role_required(Role.STUDENT)
teacher_required = role_required(Role.TEACHER, Role.ADMIN)
researcher_required = role_required(Role.RESEARCHER, Role.ADMIN)
methodist_required = role_required(Role.METHODIST, Role.ADMIN)
staff_required = role_required(Role.TEACHER, Role.METHODIST, Role.RESEARCHER, Role.ADMIN)


def can_view_student(viewer, student):
    """
    NFR-12 / FR-00 — kim kimning ma'lumotini ko'ra oladi.

    • O'zi — doim.
    • Mentor — faqat o'z guruhidagi talabani.
    • Admin — hammani. Tadqiqotchi — anonim eksport orqali (bu yerda emas).
    """
    if viewer.is_superuser:
        return True
    if viewer.pk == student.pk:
        return True
    profile = get_profile(viewer)
    if profile is None:
        return False
    if profile.role == Role.ADMIN:
        return True
    if profile.role == Role.TEACHER:
        student_profile = get_profile(student)
        return bool(
            student_profile
            and student_profile.group
            and student_profile.group.teacher_id == viewer.pk
        )
    return False


def require_student_access(viewer, student):
    if not can_view_student(viewer, student):
        raise PermissionDenied("Bu talabaning ma'lumotlarini ko'rish huquqingiz yo'q.")


def require_owner(viewer, obj, field="user"):
    """Obyekt egasi yoki unga ruxsati bor foydalanuvchini tekshiradi (IDOR himoyasi)."""
    owner = getattr(obj, field, None)
    if owner is None:
        raise PermissionDenied("Obyekt egasi aniqlanmadi.")
    require_student_access(viewer, owner)
