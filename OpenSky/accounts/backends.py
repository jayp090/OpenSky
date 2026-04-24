from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that accepts email + password.
    Uses email__iexact so the lookup is case-insensitive (e.g. User@sky.uk
    matches user@sky.uk). Falls back to None if email not found or password
    is incorrect, allowing Django to try the next backend in the list.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Accept email passed as 'email' kwarg or as the standard 'username' field
        email = kwargs.get('email') or username
        if not email:
            return None
        try:
            # Case-insensitive lookup to avoid login issues due to capitalisation
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None
        # Verify password and check the account is active
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
