from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from ..models import UserProfile, Loan, Transaction
from ..serializers.user_serializer import UserProfileSerializer
from ..serializers.loan_serializer import LoanSerializer
from ..serializers.transaction_serializer import TransactionSerializer

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        
        # Get user profile
        try:
            profile = UserProfile.objects.get(user=user)
            profile_data = UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            profile_data = {}

        # Get loan statistics
        loans = Loan.objects.filter(user=user)
        total_borrowed = loans.aggregate(Sum('amount'))['amount__sum'] or 0
        active_loans = loans.filter(status='active').count()

        # Get transaction history
        transactions = Transaction.objects.filter(user=user).order_by('-timestamp')[:5]
        recent_transactions = TransactionSerializer(transactions, many=True).data

        dashboard_data = {
            'profile': profile_data,
            'statistics': {
                'total_invested': profile_data.get('total_invested', 0),
                'total_borrowed': total_borrowed,
                'active_loans': active_loans,
            },
            'recent_transactions': recent_transactions,
        }

        return Response(dashboard_data)