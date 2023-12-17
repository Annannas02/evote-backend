from rest_framework import generics
from users import models, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from users.models import User

class UserList(generics.ListCreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_authenticated_user(request):
    # Get the JWT token from the request's cookies
    user = request.user
    serialized_data = serializers.UserSerializer(user)
    return Response(serialized_data.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_user_by_id(request, user_id):
    # Retrieve the user by ID, return 404 if not found
    user = get_object_or_404(User, pk=user_id)
    
    # Serialize the user data
    serialized_user = serializers.UserSerializer(user)
    
    # Return the user data
    return Response(serialized_user.data, status=status.HTTP_200_OK)
   