# serializers/auth_serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from ..models.auth_models import UserProfile, PhoneVerification, IDVerification

class PhoneVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneVerification
        fields = ['phone_number', 'is_verified']

class IDVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IDVerification
        fields = ['id_number', 'is_verified']

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
        return cleaned_number

    def validate_id_number(self, value):
        # Add your ID number validation logic here
        if IDVerification.objects.filter(id_number=value).exists():
            raise serializers.ValidationError("This ID number is already registered")
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

class SimpleEmailRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered")
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    phone_verification = PhoneVerificationSerializer(source='user.phoneverification', read_only=True)
    id_verification = IDVerificationSerializer(source='user.idverification', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'verification_method',
            'credit_score',
            'total_invested',
            'total_borrowed',
            'active_investments',
            'phone_verification',
            'id_verification'
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']