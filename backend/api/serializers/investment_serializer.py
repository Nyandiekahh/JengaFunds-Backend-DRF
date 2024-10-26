# api/serializers/investment_serializer.py
from rest_framework import serializers
from ..models.investment import LoanInvestment
from django.db.models import Sum

class LoanInvestmentSerializer(serializers.ModelSerializer):
    investor_name = serializers.SerializerMethodField()
    loan_details = serializers.SerializerMethodField()
    
    class Meta:
        model = LoanInvestment
        fields = [
            'id',
            'loan',
            'loan_details',
            'amount',
            'payment_method',
            'status',
            'created_at',
            'investor_name',
            'payment_reference'
        ]
        read_only_fields = ['status', 'created_at', 'investor_name', 'payment_reference']

    def get_investor_name(self, obj):
        return obj.investor.username

    def get_loan_details(self, obj):
        from .loan_serializer import LoanSerializer
        return LoanSerializer(obj.loan).data

    def validate(self, data):
        loan = data['loan']
        amount = data['amount']
        
        # Check if loan is available for investment
        if loan.status not in ['Available', 'Funding']:
            raise serializers.ValidationError(
                "This loan is not available for investment"
            )
        
        # Calculate remaining amount needed
        total_invested = loan.investments.filter(
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        remaining_amount = float(loan.amount) - total_invested
        
        # Check if investment amount is valid
        if amount > remaining_amount:
            raise serializers.ValidationError(
                f"Maximum investment amount available is {remaining_amount}"
            )
        
        if amount < 1000:  # Minimum investment amount
            raise serializers.ValidationError(
                "Minimum investment amount is KES 1,000"
            )
        
        return data

    def create(self, validated_data):
        # Set investor to current user
        validated_data['investor'] = self.context['request'].user
        return super().create(validated_data)