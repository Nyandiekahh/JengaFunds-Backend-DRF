# api/serializers/loan_serializer.py
from rest_framework import serializers
from ..models import Loan, LoanType
from .user_serializer import UserProfileSerializer
from django.db.models import Sum

class LoanTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanType
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    loan_type_name = serializers.CharField(source='loan_type.name', read_only=True)
    borrower = serializers.SerializerMethodField()
    credit_score = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    monthly_payment = serializers.SerializerMethodField()
    total_return = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    risk_level = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            'id', 
            'user', 
            'loan_type', 
            'loan_type_name', 
            'amount',
            'status', 
            'created_at', 
            'interest_rate', 
            'term_months',
            'borrower',
            'credit_score',
            'progress',
            'monthly_payment',
            'total_return',
            'documents',
            'risk_level',
            'purpose',
            'description'
        ]
        read_only_fields = ['progress', 'monthly_payment', 'total_return', 'risk_level']
        extra_kwargs = {
            'user': {'write_only': True}  # Hide user field in response
        }

    def get_borrower(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'name': f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        }

    def get_credit_score(self, obj):
        try:
            return obj.user.userprofile.credit_score
        except:
            return 600  # Default credit score

    def get_progress(self, obj):
        # Calculate progress based on total investments
        try:
            total_invested = obj.investments.filter(
                status='completed'
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            return round((total_invested / float(obj.amount)) * 100, 2)
        except:
            return 0

    def get_monthly_payment(self, obj):
        # Calculate monthly payment using simple interest
        total_interest = float(obj.amount) * (float(obj.interest_rate) / 100) * (obj.term_months / 12)
        total_amount = float(obj.amount) + total_interest
        return round(total_amount / obj.term_months, 2)

    def get_total_return(self, obj):
        # Calculate total return (principal + interest)
        total_interest = float(obj.amount) * (float(obj.interest_rate) / 100) * (obj.term_months / 12)
        return round(float(obj.amount) + total_interest, 2)

    def get_documents(self, obj):
        # If you have a documents related model, you can add it here
        # For now, returning empty list or dummy data
        return []

    def get_risk_level(self, obj):
        # Calculate risk level based on credit score
        credit_score = self.get_credit_score(obj)
        if credit_score >= 750:
            return 'Low'
        elif credit_score >= 650:
            return 'Medium'
        else:
            return 'High'

    def validate(self, data):
        # Validate loan amount against loan type max amount
        if data.get('loan_type') and data.get('amount'):
            if data['amount'] > data['loan_type'].max_amount:
                raise serializers.ValidationError(
                    f"Loan amount cannot exceed {data['loan_type'].max_amount}"
                )

        # You can add more validations here
        return data

    def create(self, validated_data):
        # Set initial status to 'Available'
        validated_data['status'] = 'Available'
        return super().create(validated_data)