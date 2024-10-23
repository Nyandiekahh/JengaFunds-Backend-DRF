from django.contrib import admin
from .models import (
    UserProfile, Loan, LoanType, Transaction,
    PhoneVerification, IDVerification, RegistrationProfile
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'credit_score', 'total_invested', 'total_borrowed')
    search_fields = ('user__username',)

@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_amount', 'interest_rate', 'term_months')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'loan_type', 'amount', 'status', 'created_at')
    list_filter = ('status', 'loan_type')
    search_fields = ('user__username',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'amount', 'timestamp')
    list_filter = ('type', 'timestamp')
    search_fields = ('user__username', 'description')

# Add the new model registrations
@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_verified', 'created_at')
    list_filter = ('is_verified',)
    search_fields = ('user__username', 'phone_number')

@admin.register(IDVerification)
class IDVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'id_number', 'is_verified', 'verification_date')
    list_filter = ('is_verified',)
    search_fields = ('user__username', 'id_number')

@admin.register(RegistrationProfile)
class RegistrationProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_method', 'registration_complete', 'registration_date')
    list_filter = ('verification_method', 'registration_complete')
    search_fields = ('user__username',)