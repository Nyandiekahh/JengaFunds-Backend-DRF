from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Loan, LoanType
from ..serializers.loan_serializer import LoanSerializer, LoanTypeSerializer

class LoanViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LoanSerializer

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LoanTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LoanType.objects.all()
    serializer_class = LoanTypeSerializer