from rest_framework import generics
from users import models, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status
import jwt
from evoteapp.settings import JWT_SECRET
from users.models import User

class UserList(generics.ListCreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_authenticated_user(request):
    # Get the JWT token from the request's cookies
    jwt_token = request.COOKIES.get('Authentication')

    if not jwt_token:
        return Response(
            {"error": "JWT token not found."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Decode the JWT token
        decoded_token = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        user_id = decoded_token['user_id']

        # Retrieve the User object from the database
        user = User.objects.get(pk=user_id)

        return Response({user}, status=status.HTTP_200_OK)

    except jwt.ExpiredSignatureError:
        return Response(
            {"error": "JWT token has expired."},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except jwt.InvalidTokenError:
        return Response(
            {"error": "Invalid JWT token."},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except User.DoesNotExist:
        return Response(
            {"error": "User not found."},
            status=status.HTTP_404_NOT_FOUND
        )