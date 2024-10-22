from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from ..models import UserProfile
from ..serializers.user_serializer import UserSerializer
from google.oauth2 import id_token
from google.auth.transport import requests

def send_verification_email(user, verification_url):
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #f9f9f9; padding: 20px; border-radius: 10px;">
                <h2 style="color: #333; text-align: center;">Welcome to JengaFunds!</h2>
                <p>Hello {user.first_name},</p>
                <p>Thank you for registering with JengaFunds. To complete your registration and verify your email address, please click the button below:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Verify Email Address
                    </a>
                </div>
                <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                <p style="background-color: #eee; padding: 10px; border-radius: 5px;">{verification_url}</p>
                <p>This verification link will expire in 24 hours.</p>
                <hr style="border: 1px solid #eee; margin: 20px 0;">
                <p style="color: #666; font-size: 12px; text-align: center;">
                    If you didn't register for a JengaFunds account, you can safely ignore this email.
                </p>
            </div>
        </body>
    </html>
    """
    
    send_mail(
        subject='Verify your JengaFunds account',
        message=f'Click this link to verify your email: {verification_url}',
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

def send_password_reset_email(user, reset_url):
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #f9f9f9; padding: 20px; border-radius: 10px;">
                <h2 style="color: #333; text-align: center;">Reset Your Password</h2>
                <p>Hello {user.first_name},</p>
                <p>We received a request to reset your JengaFunds account password. Click the button below to reset it:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Reset Password
                    </a>
                </div>
                <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                <p style="background-color: #eee; padding: 10px; border-radius: 5px;">{reset_url}</p>
                <p>This password reset link will expire in 24 hours.</p>
                <hr style="border: 1px solid #eee; margin: 20px 0;">
                <p style="color: #666; font-size: 12px; text-align: center;">
                    If you didn't request a password reset, you can safely ignore this email.
                </p>
            </div>
        </body>
    </html>
    """
    
    send_mail(
        subject='Reset your JengaFunds password',
        message=f'Click this link to reset your password: {reset_url}',
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        data = request.data
        if User.objects.filter(email=data['email']).exists():
            return Response(
                {'error': 'User with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            is_active=False
        )
        
        UserProfile.objects.create(user=user)
        
        token = default_token_generator.make_token(user)
        verification_url = f"http://localhost:3000/verify-email/{user.id}/{token}"
        
        send_verification_email(user, verification_url)
        
        return Response({
            'message': 'Registration successful. Please check your email to verify your account.',
            'user_id': user.id
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(username=email, password=password)
        if not user:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        if not user.is_active:
            return Response(
                {'error': 'Please verify your email first'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    try:
        user_id = request.data.get('user_id')
        token = request.data.get('token')
        
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Email verified successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            })
        return Response(
            {'error': 'Invalid verification link'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    try:
        email = request.data.get('email')
        user = User.objects.get(email=email)
        
        token = default_token_generator.make_token(user)
        reset_url = f"http://localhost:3000/reset-password/{user.id}/{token}"
        
        send_password_reset_email(user, reset_url)
        
        return Response({
            'message': 'Password reset instructions sent to your email'
        })
    except User.DoesNotExist:
        # Return success even if user doesn't exist (security best practice)
        return Response({
            'message': 'If an account exists with this email, you will receive password reset instructions.'
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    try:
        user_id = request.data.get('user_id')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password reset successful'})
        return Response(
            {'error': 'Invalid reset link'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    try:
        token = request.data.get('token')
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        )

        email = idinfo['email']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True
            }
        )
        
        if created:
            UserProfile.objects.create(user=user)
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        })
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    
    if not user.check_password(current_password):
        return Response(
            {'error': 'Current password is incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password changed successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logged out successfully'})
    except Exception:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)