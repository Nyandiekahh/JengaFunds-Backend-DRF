from rest_framework import serializers
from ..models import Loan, LoanType

class LoanTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanType
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    loan_type_name = serializers.CharField(source='loan_type.name', read_only=True)
    
    class Meta:
        model = Loan
        fields = ['id', 'user', 'loan_type', 'loan_type_name', 'amount', 
                 'status', 'created_at', 'interest_rate', 'term_months']