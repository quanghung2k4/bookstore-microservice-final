from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.application.use_cases import UserService
from users.infrastructure.models import UserModel
from users.infrastructure.repositories import DjangoUserRepository
from users.presentation.serializers import LoginSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    lookup_field = "id"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService(DjangoUserRepository()).create_user(dict(serializer.validated_data))
        return Response(self.get_serializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def profile(self, request, id=None):
        return Response(self.get_serializer(self.get_object()).data)

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService(DjangoUserRepository()).login(**serializer.validated_data)
        return Response(self.get_serializer(user).data)
