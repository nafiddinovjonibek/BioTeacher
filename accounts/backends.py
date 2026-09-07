"""Email yoki username orqali kirish (FR-01)."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        login_value = (username or kwargs.get("email") or "").strip()
        if not login_value or not password:
            return None
        try:
            user = User.objects.get(Q(email__iexact=login_value) | Q(username__iexact=login_value))
        except User.DoesNotExist:
            # Vaqt hujumiga qarshi — baribir hash hisoblaymiz.
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            user = User.objects.filter(email__iexact=login_value).first()
            if user is None:
                return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
