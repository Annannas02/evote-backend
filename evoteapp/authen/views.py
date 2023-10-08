
from django.contrib.auth import hashers
from rest_framework import generics, status, response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from authen import serializers
from users import models
from sendsms import api 
import pyotp
from rest_framework.response import Response
#usage api.send_sms(body='I can haz txt', from_phone='+41791111111', to=['+41791234567'])
from evoteapp import settings
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
    secret = request.data.get('secret')

    if not secret:
        return Response(
            {"error": "Secret key is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:

        totp = pyotp.TOTP(secret)
        totp_code = totp.now()
        return Response(totp_code, status=status.HTTP_200_OK)

    except pyotp.utils.OtpError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
# VALIDATION OF INPUTTED OTP VS GIVEN OTP
    
@api_view(['POST'])
def authenticate_2fa(request):
    otp = request.data.get('otp')

    if not otp:
        return Response(
            {"error": "OTP is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user

    try:
        totp = pyotp.TOTP(user.secret)

        current_otp = totp.now()

        if otp == current_otp:
            return Response({"message": "Authentication successful."}, status=status.HTTP_200_OK)
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