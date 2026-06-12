from rest_framework import serializers

from users.infrastructure.models import UserModel


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = UserModel
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "role",
            "is_verified",
            "is_active",
        ]
        read_only_fields = ["id"]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
