# api/serializers/dashboard_serializer.py
from rest_framework import serializers

class StatItemSerializer(serializers.Serializer):
    value = serializers.CharField()
    change = serializers.CharField()

class DashboardStatsSerializer(serializers.Serializer):
    total_invested = StatItemSerializer()
    total_borrowed = StatItemSerializer()
    active_investments = StatItemSerializer()
    avg_return_rate = StatItemSerializer()

# api/views/dashboard_views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg
from django.db.models.functions import Coalesce
from decimal import Decimal

from ..models import LoanInvestment, Loan
from ..serializers.dashboard_serializer import DashboardStatsSerializer

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        user = request.user
        
        # Calculate total invested amount
        total_invested = LoanInvestment.objects.filter(
            investor=user,
            status='completed'
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']

        # Calculate total borrowed amount
        total_borrowed = Loan.objects.filter(
            user=user,
            status='Funded'
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']

        # Calculate active investments count
        active_investments = LoanInvestment.objects.filter(
            investor=user,
            status='completed',
            loan__status='Funding'
        ).count()

        # Calculate average return rate
        investments = LoanInvestment.objects.filter(
            investor=user,
            status='completed',
            loan__status__in=['Funding', 'Funded']
        ).select_related('loan')
        
        total_return_rate = Decimal('0')
        investment_count = 0
        
        for investment in investments:
            if investment.loan.interest_rate:
                total_return_rate += investment.loan.interest_rate
                investment_count += 1
        
        avg_return_rate = (total_return_rate / investment_count) if investment_count > 0 else Decimal('0')

        # Calculate changes (you'll need to implement your own logic for historical comparison)
        stats = {
            'total_invested': {
                'value': f"KES {total_invested:,.2f}",
                'change': '+5.2%'  # Replace with actual calculation
            },
            'total_borrowed': {
                'value': f"KES {total_borrowed:,.2f}",
                'change': '-2.1%'  # Replace with actual calculation
            },
            'active_investments': {
                'value': str(active_investments),
                'change': '+1'  # Replace with actual calculation
            },
            'avg_return_rate': {
                'value': f"{avg_return_rate:.1f}%",
                'change': '+0.3%'  # Replace with actual calculation
            }
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)