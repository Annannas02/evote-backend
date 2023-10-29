
from django.contrib.auth import hashers
from rest_framework import generics, status, response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.utils import timezone
from authen import serializers
from otp.models import OTP
from datetime import datetime, timedelta
from users import models as usermodels
from tokens.models import Token
from sendsms import api 
import pyotp
from rest_framework.response import Response
#usage api.send_sms(body='I can haz txt', from_phone='+41791111111', to=['+41791234567'])
from evoteapp import settings
from jwt import encode
import hashlib
import random
import datetime 
from rest_framework.permissions import AllowAny, IsAuthenticated

#REGISTRATION

JWT_SECRET="M3ljN0IzPmgvaWhrZGRDXCpYMzkjWC0="

class RegisterUserView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    serializer_class = serializers.RegisterUserSerializer

#GENERATION OF TOTP

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_totp(request):
    secret = request.data.get('secret')

    if not secret:
        return Response(
            {"error": "Secret key is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create a TOTP instance with the provided secret
        totp = pyotp.TOTP(secret)
        totp_code = totp.now()

        user = usermodels.User.objects.get(id=request.user.id)
        
        # Attempt to get an existing OTP entry for the user
        otp_entry, created = OTP.objects.get_or_create(personid=user)

        # Update the timestamp, whether it's a new entry or an existing one
        otp_entry.timestamp = timezone.now()
        otp_entry.phone = user.phone
        otp_entry.save()

        return Response({"totp_code": totp_code}, status=status.HTTP_200_OK)

    except pyotp.utils.OtpError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
# VALIDATION OF INPUTTED OTP VS GIVEN OTP
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def authenticate_2fa(request):
    otp = request.data.get('otp')

    if not otp:
        return Response(
            {"error": "OTP is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user

    try:
        # Verify if the user has an associated OTP entry
        otp_entry = OTP.objects.filter(personid=user).first()

        if not otp_entry:
            return Response(
                {"error": "No OTP entry found for the user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a TOTP instance with the user's stored secret
        totp = pyotp.TOTP(user.secret)

        # Get the OTP generated at the current moment
        current_otp = totp.now()

        # Compare the provided OTP with the OTP associated with the timestamp in the database
        if otp == current_otp:
            # If OTP is correct, create a JWT token with user ID and a 1-day expiration
            expiration_time = datetime.utcnow() + timedelta(days=1)
            payload = {
                "user_id": user.id,
                "exp": expiration_time
            }
            jwt_token = encode(payload, JWT_SECRET, algorithm='HS256')
            cookie_value = f"Authentication={jwt_token}; HttpOnly; Path=/; Max-Age={expiration_time}"
            # Set the JWT token in the response header
            response = Response({"message": "Authentication successful."}, status=status.HTTP_200_OK)
            response['Set-Cookie'] = cookie_value
            return response
        else:
            return Response(
                {"error": "Invalid OTP. Authentication failed."},
                status=status.HTTP_401_UNAUTHORIZED
            )

    except pyotp.utils.OtpError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    

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
    secret_salt = "your_secret_salt_here"  
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