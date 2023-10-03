from rest_framework import generics
from users import models, serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser


class UserList(generics.ListCreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
