from django.db import models
from django.contrib.auth.models import User
from .user_profile import UserProfile

class PhoneVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='phone_verification')
    phone_number = models.CharField(max_length=15, unique=True)
    verification_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'api'
        db_table = 'api_phone_verification'
        verbose_name = 'Phone Verification'
        verbose_name_plural = 'Phone Verifications'

    def __str__(self):
        return f"Phone verification for {self.user.username}"

    def save(self, *args, **kwargs):
        # If phone is verified, update the associated UserProfile
        if self.is_verified and hasattr(self.user, 'userprofile'):
            profile = self.user.userprofile
            profile.save()
        super().save(*args, **kwargs)

class IDVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='id_verification')
    id_number = models.CharField(max_length=20, unique=True)
    id_type = models.CharField(
        max_length=20,
        choices=[
            ('national_id', 'National ID'),
            ('passport', 'Passport'),
            ('alien_id', 'Alien ID')
        ],
        default='national_id'
    )
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verification_document = models.FileField(
        upload_to='id_verification_docs/',
        null=True,
        blank=True
    )

    class Meta:
        app_label = 'api'
        db_table = 'api_id_verification'
        verbose_name = 'ID Verification'
        verbose_name_plural = 'ID Verifications'

    def __str__(self):
        return f"ID verification for {self.user.username}"

    def save(self, *args, **kwargs):
        # If ID is verified, update the associated UserProfile
        if self.is_verified and hasattr(self.user, 'userprofile'):
            profile = self.user.userprofile
            profile.save()
        super().save(*args, **kwargs)

class RegistrationProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='registration_profile')
    verification_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('simple', 'Simple Email')
        ],
        default='email'
    )
    registration_complete = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_verification_attempt = models.DateTimeField(null=True, blank=True)
    next_allowed_attempt = models.DateTimeField(null=True, blank=True)
    verification_attempts = models.IntegerField(default=0)
    referral_code = models.CharField(max_length=20, null=True, blank=True)
    terms_accepted = models.BooleanField(default=False)
    privacy_accepted = models.BooleanField(default=False)

    class Meta:
        app_label = 'api'
        db_table = 'api_registration_profile'
        verbose_name = 'Registration Profile'
        verbose_name_plural = 'Registration Profiles'

    def __str__(self):
        return f"Registration profile for {self.user.username}"

    def save(self, *args, **kwargs):
        if self.registration_complete and hasattr(self.user, 'userprofile'):
            profile = self.user.userprofile
            profile.save()
        super().save(*args, **kwargs)