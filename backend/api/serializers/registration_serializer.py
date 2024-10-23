from rest_framework import serializers
from django.contrib.auth.models import User
from ..models.auth_models import UserProfile, PhoneVerification, IDVerification

class PhoneRegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    id_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def validate_phone_number(self, value):
        # Remove any spaces or special characters
        cleaned_number = ''.join(filter(str.isdigit, value))
        if len(cleaned_number) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")
        if PhoneVerification.objects.filter(phone_number=cleaned_number).exists():
            raise serializers.ValidationError("This phone number is already registered")
        return cleaned_number

    def validate_id_number(self, value):
        cleaned_id = ''.join(filter(str.isdigit, value))
        if not 7 <= len(cleaned_id) <= 8:
            raise serializers.ValidationError("ID number must be 7 or 8 digits")
        if IDVerification.objects.filter(id_number=cleaned_id).exists():
            raise serializers.ValidationError("This ID number is already registered")
        return cleaned_id

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return value

class EmailRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return value

class SimpleEmailRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return value