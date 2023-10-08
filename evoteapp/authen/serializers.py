from rest_framework import serializers
from users import models
from django.contrib.auth import hashers
from phonenumber_field.phonenumber import PhoneNumber
from users.serializers import UserSerializer
import pyotp


class RegisterUserSerializer(serializers.Serializer):
    idnp = serializers.CharField()
    phone = PhoneNumber() # Use PhoneNumberField for phone input

    """ future validation through official idnp list
    def validate(self, attrs):
        if attrs['idnp'] != attrs['confirm_idnp']:
            raise serializers.ValidationError('The IDNP values do not coincide.')

        return attrs
    """

    def create(self, validated_data):
        # Hash the idnp value before saving
        hashed_idnp = hashers.make_password(validated_data['idnp'])
        secret = pyotp.random_base32()
        user = models.User.objects.create(idnp=hashed_idnp, phone=validated_data['phone'], secret=validated_data['secret'])
        return user




    
