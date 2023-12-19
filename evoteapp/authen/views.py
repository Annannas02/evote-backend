from django.contrib.auth import hashers
from rest_framework import generics, status, response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.utils import timezone
from otp.models import OTP
from users.serializers import UserSerializer
from tokens.serializers import TokenSerializer
from evoteapp.settings import SECRET_SALT
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
from rest_framework_simplejwt.tokens import RefreshToken
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    idnp = request.data.get("idnp")
    phone = request.data.get("phone")

    hashed_idnp = hashers.make_password(idnp)
    secret = pyotp.random_base32()
    
    user = usermodels.User.objects.create(
        idnp=hashed_idnp,
        phone=phone,
        secret=secret,
        date_generate_token=None
    )
    user_serialized = UserSerializer(user)
    return Response({"message" : "User created successfully", "user": user_serialized.data}, status=status.HTTP_200_OK)

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

    try:
    # Verify if the user has an associated OTP entry
        otp_entry = OTP.objects.filter(personid=user).first()

        if not otp_entry:
            return Response(
                {"error": "No OTP entry found for the user."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        totp = pyotp.TOTP(user.secret)

        # Compare the provided OTP with the OTP associated with the timestamp in the database
        if otp==totp.at(for_time=otp_entry.timestamp):
            
            refresh = RefreshToken.for_user(user=user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return response.Response(
                {'tokens': tokens},
                status=status.HTTP_202_ACCEPTED
            )
        else:
            return Response(
                {"error": "Invalid OTP. Authentication failed."},
                status=status.HTTP_401_UNAUTHORIZED
            )


    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    

#USER TOKEN GENERATION
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_token(request):
    try:
        user = usermodels.User.objects.get(id=request.data.get("id"))
        if request.user != user:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        

        # Generate the token value as a concatenation of idnp, phone, and a secret salt
        token_value = f"{user.idnp}{user.phone}{SECRET_SALT}"

        # Calculate the MD5 hash of the token value
        token_hash = hashlib.md5(token_value.encode()).hexdigest()[:6]

        # Check if a token with the same value already exists
        existing_token = Token.objects.filter(token_value=token_hash).first()

        if user.got_token or existing_token:
            return Response(
                {"error": "Token already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create or update the user's record to mark that they have received a token
        usermodels.User.objects.filter(pk=user.pk).update(got_token=True, date_generate_token=timezone.now())

        # Create a new token entry in the Token table
        new_token = Token.objects.create(personid=user, token_value=token_hash, voted=False, date_voted=None)

        token_serialized = TokenSerializer(new_token)
        return Response({"message": "Token generated successfully.", "token" : token_serialized.data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST        
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_token(request):

    token = request.data.get("token_value")
    
    try:

            # Check if the user has an associated token in the Token table
        user_token = Token.objects.filter(token_value=token).first()
        print(user_token.personid)

        if user_token:
            user = usermodels.User.objects.get(idnp=user_token.personid)
            user_serialized = UserSerializer(user)
            return Response({"message": "User token is verified.", "user": user_serialized.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "User token wrong."},
                status=status.HTTP_401_UNAUTHORIZED
            )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
            
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def send_sms(request):
    phone_to = request.data.get("to")
    data = request.data.get("data")
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_nr = os.getenv('FROM_TEL_NR')
        client = Client(account_sid, auth_token)

        if not phone_to:
            return Response(
                    {"error": "Invalid phone number!"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not data:
            return Response(
                    {"error": "Invalid message body!"},
                    status=status.HTTP_400_BAD_REQUEST
                )


        message = client.messages \
            .create(
                body=data,
                from_=from_nr,
                to=phone_to
            )
        return Response({"message": f"Sent SMS successfully to {phone_to}"}, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )