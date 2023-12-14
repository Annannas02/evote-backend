from rest_framework import generics
from users import models, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status

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

   