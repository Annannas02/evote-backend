from django.contrib.auth import hashers
from rest_framework import generics, status, response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.utils import timezone
from authen import serializers
from otp.models import OTP
from evoteapp.settings import JWT_SECRET
from datetime import datetime, timedelta
from users import models as usermodels
from tokens.models import Token
from textmagic.rest import TextmagicRestClient
import pyotp
from rest_framework.response import Response
import jwt
import hashlib
import random
import datetime 
from rest_framework.permissions import AllowAny, IsAuthenticated

#REGISTRATION
class RegisterUserView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    serializer_class = serializers.RegisterUserSerializer


#GENERATION OF TOTP
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_totp(request):
    try:
        try:
            user = usermodels.User.objects.get(id=request.data.get("id"))

        except user.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        secret = user.secret
        if not secret:
            return Response(
                {"error": "Secret key is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a TOTP instance with the provided secret
        totp = pyotp.TOTP(secret)
        totp_code = totp.now()
        
        # Attempt to get an existing OTP entry for the user
        otp_entry = OTP.objects.filter(personid=user).first()

        if otp_entry:
            # Update the timestamp and phone for the existing entry
            otp_entry.timestamp = timezone.now()
            otp_entry.phone = user.phone
            otp_entry.save()
        else:
            # Create a new OTP entry if none exists
            OTP.objects.create(personid=user, timestamp=timezone.now(), phone=user.phone)
            

            #, "user_id": user.id
        return Response({"totp_code": totp_code}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
        
        
    

# VALIDATION OF INPUTTED OTP VS GIVEN OTP
@api_view(['POST'])
@permission_classes([AllowAny])
def authenticate_2fa(request):
    otp = request.data.get('totp_code')


    if not otp:
        return Response(
            {"error": "OTP is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = usermodels.User.objects.get(id=request.data.get("id"))

    #try:
    # Verify if the user has an associated OTP entry
    otp_entry = OTP.objects.filter(personid=user).first()

    if not otp_entry:
        return Response(
            {"error": "No OTP entry found for the user."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Compare the provided OTP with the OTP associated with the timestamp in the database
    if pyotp.TOTP.verify(self=pyotp.TOTP,otp=otp, for_time=otp_entry.timestamp):
        print('yay')
    else:
        print('oh no!')


"""
            # If OTP is correct, create a JWT token with user ID and a 1-day expiration
            expiration_time = datetime.utcnow() + timedelta(days=1)
            payload = {
                "user_id": user.id,
                "exp": expiration_time
            }
            jwt_token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
            cookie_value = f"Authentication={jwt_token}; HttpOnly; Path=/; Max-Age={expiration_time}"
            # Set the JWT token in the response header
            response = Response({"message": "Authentication successful."}, status=status.HTTP_200_OK)
            response['Set-Cookie'] = cookie_value
            return response
        else:
            return Response(
                {"error": "Invalid OTP. Authentication failed."},
                status=status.HTTP_401_UNAUTHORIZED
            )"""

"""
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
            
        )"""
    

#USER TOKEN GENERATION
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_token(request):
    user = request.user

    if user.got_token:
        return Response(
            {"error": "Token already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Generate the token value as a concatenation of idnp, phone, and a secret salt
    secret_salt = "pKc:t#ihYK6Id=/r"  
    token_value = f"{user.idnp}{user.phone}{secret_salt}"

    # Calculate the MD5 hash of the token value
    token_hash = hashlib.md5(token_value.encode()).hexdigest()

    # Create or update the user's record to mark that they have received a token
    usermodels.User.objects.filter(pk=user.pk).update(got_token=True)

    # Check if a token with the same value already exists
    existing_token = Token.objects.filter(token_value=token_hash).first()

    if existing_token:
        return Response(
            {"message": "Token already exists."},
            status=status.HTTP_200_OK
        )

    # Create a new token entry in the Token table
    new_token = Token.objects.create(person=user, token_value=token_hash, voted=False, date_voted=None)

    return Response({"message": "Token generated successfully."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    user = request.user

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

        # Verify if the decoded user_id matches the authenticated user's ID
        if user.id == user_id:
            # Check if the user has an associated token in the Token table
            user_token = Token.objects.filter(person=user).first()

            if user_token == request.token:
                return Response({"message": "User token is verified."}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "User token wrong."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(
                {"error": "Mismatched user ID in the JWT token."},
                status=status.HTTP_401_UNAUTHORIZED
            )

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
