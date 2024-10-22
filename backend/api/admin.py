from django.contrib import admin
from .models import UserProfile, Loan, LoanType, Transaction

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