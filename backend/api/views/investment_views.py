from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q
from ..models import LoanInvestment, Loan
from ..serializers.investment_serializer import LoanInvestmentSerializer

class InvestmentViewSet(viewsets.ModelViewSet):
    serializer_class = LoanInvestmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can see their investments and investments in their loans
        return LoanInvestment.objects.filter(
            Q(investor=self.request.user) | Q(loan__user=self.request.user)
        ).select_related('loan', 'investor')

    def perform_create(self, serializer):
        loan_id = self.request.data.get('loan')
        loan = get_object_or_404(Loan, id=loan_id)
        
        # Check if loan is available for investment
        if loan.status not in ['Available', 'Funding']:
            return Response(
                {'error': 'This loan is not available for investment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create investment
        investment = serializer.save(
            investor=self.request.user,
            loan=loan
        )

        # Handle payment method
        payment_method = self.request.data.get('payment_method')
        
        if payment_method == 'mpesa':
            return self._handle_mpesa_payment(investment)
        elif payment_method == 'bank':
            return self._handle_bank_transfer(investment)
        elif payment_method == 'card':
            return self._handle_card_payment(investment)

    def _handle_mpesa_payment(self, investment):
        # Integrate with your existing M-Pesa implementation
        return Response({
            'status': 'pending',
            'message': 'M-Pesa payment initiated',
            'investment_id': investment.id
        })

    def _handle_bank_transfer(self, investment):
        return Response({
            'status': 'pending',
            'message': 'Bank transfer initiated',
            'investment_id': investment.id,
            'bank_details': {
                'bank_name': 'Your Bank Name',
                'account_number': '1234567890',
                'reference': f'INV-{investment.id}'
            }
        })

    def _handle_card_payment(self, investment):
        return Response({
            'status': 'pending',
            'message': 'Card payment initiated',
            'investment_id': investment.id,
            'payment_url': f'/api/payments/card/{investment.id}'
        })

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        investment = self.get_object()
        
        # Verify payment (implement your payment verification logic)
        # For demonstration, we'll just update the status
        investment.status = 'completed'
        investment.save()
        
        return Response({
            'status': 'success',
            'message': 'Payment confirmed successfully'
        })