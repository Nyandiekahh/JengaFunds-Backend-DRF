# api/views/loan_application_views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Loan
from .serializers import LoanSerializer

class ApplyForLoanView(generics.CreateAPIView):
    queryset = Loan.objects.all()  # Get all Loan instances
    serializer_class = LoanSerializer  # Specify the serializer for Loan
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can apply

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Associate the loan with the logged-in user
