from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Transaction
from ..serializers.transaction_serializer import TransactionSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)