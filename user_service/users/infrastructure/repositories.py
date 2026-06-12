from rest_framework.exceptions import AuthenticationFailed

from users.infrastructure.models import UserModel


class DjangoUserRepository:
    def create(self, data):
        password = data.pop("password")
        user = UserModel(**data)
        user.set_password(password)
        user.is_staff = user.role in {"admin", "staff"}
        user.is_superuser = user.role == "admin"
        user.save()
        return user

    def authenticate(self, username, password):
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist as exc:
            raise AuthenticationFailed("Invalid username or password.") from exc

        if not user.check_password(password):
            raise AuthenticationFailed("Invalid username or password.")
        return user
