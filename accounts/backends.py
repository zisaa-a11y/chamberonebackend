from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    """Authenticate using email address instead of username."""

    def authenticate(self, request, email=None, password=None, username=None, **kwargs):
        # Support both 'email' and 'username' keyword args
        lookup = email or username
        if lookup is None:
            return None
        try:
            user = User.objects.get(email=lookup)
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
