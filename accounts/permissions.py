"""
Rolga asoslangan ruxsat dekoratorlari va obyekt darajasidagi tekshiruvlar (NFR-12).

Qoida FR-00: o'qituvchi boshqa o'qituvchining natijasini hech qachon ko'rmaydi.
Kontent va boshqa foydalanuvchilarning ma'lumoti — faqat ADMIN qo'lida.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from core.enums import Role


def get_profile(user):
    return getattr(user, "profile", None)


def has_role(user, *roles):
    """Faol rol bo'yicha tekshiradi (superuser — hamma joyga kiradi)."""
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


# Har qanday ro'yxatdan o'tgan foydalanuvchi (o'rganuvchi yoki admin).
teacher_required = role_required(Role.TEACHER, Role.ADMIN)
# Faqat CRUD huquqiga ega rol.
admin_required = role_required(Role.ADMIN)


def can_view_student(viewer, student):
    """
    NFR-12 / FR-00 — kim kimning ma'lumotini ko'ra oladi.

    • O'zi — doim.
    • Admin — hammani.
    • Boshqa o'qituvchi — hech qachon.
    """
    if viewer.is_superuser:
        return True
    if viewer.pk == student.pk:
        return True
    profile = get_profile(viewer)
    return bool(profile and profile.role == Role.ADMIN)


def require_student_access(viewer, student):
    if not can_view_student(viewer, student):
        raise PermissionDenied("Bu foydalanuvchining ma'lumotlarini ko'rish huquqingiz yo'q.")


def require_owner(viewer, obj, field="user"):
    """Obyekt egasi yoki unga ruxsati bor foydalanuvchini tekshiradi (IDOR himoyasi)."""
    owner = getattr(obj, field, None)
    if owner is None:
        raise PermissionDenied("Obyekt egasi aniqlanmadi.")
    require_student_access(viewer, owner)
