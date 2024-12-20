# Generated by Django 5.1.2 on 2024-10-22 23:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='IDVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_number', models.CharField(max_length=20, unique=True)),
                ('id_type', models.CharField(choices=[('national_id', 'National ID'), ('passport', 'Passport'), ('alien_id', 'Alien ID')], default='national_id', max_length=20)),
                ('is_verified', models.BooleanField(default=False)),
                ('verification_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('verification_document', models.FileField(blank=True, null=True, upload_to='id_verification_docs/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='id_verification', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'ID Verification',
                'verbose_name_plural': 'ID Verifications',
                'db_table': 'api_id_verification',
            },
        ),
        migrations.CreateModel(
            name='PhoneVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=15, unique=True)),
                ('verification_code', models.CharField(max_length=6)),
                ('is_verified', models.BooleanField(default=False)),
                ('attempts', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='phone_verification', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Phone Verification',
                'verbose_name_plural': 'Phone Verifications',
                'db_table': 'api_phone_verification',
            },
        ),
        migrations.CreateModel(
            name='RegistrationProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verification_method', models.CharField(choices=[('email', 'Email'), ('phone', 'Phone'), ('simple', 'Simple Email')], default='email', max_length=20)),
                ('registration_complete', models.BooleanField(default=False)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('last_verification_attempt', models.DateTimeField(blank=True, null=True)),
                ('next_allowed_attempt', models.DateTimeField(blank=True, null=True)),
                ('verification_attempts', models.IntegerField(default=0)),
                ('referral_code', models.CharField(blank=True, max_length=20, null=True)),
                ('terms_accepted', models.BooleanField(default=False)),
                ('privacy_accepted', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='registration_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Registration Profile',
                'verbose_name_plural': 'Registration Profiles',
                'db_table': 'api_registration_profile',
            },
        ),
    ]
