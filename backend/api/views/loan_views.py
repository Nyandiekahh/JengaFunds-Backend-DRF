from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
import logging

from ..models import Loan, LoanType
from ..serializers.loan_serializer import LoanSerializer, LoanTypeSerializer
from ..serializers.document_serializer import DocumentSerializer

logger = logging.getLogger(__name__)

class LoanPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class LoanViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LoanSerializer

    def get_queryset(self):
        print(f"\n=== Debug Info ===")
        print(f"Current user: {self.request.user.username}")
        print(f"Is staff: {self.request.user.is_staff}")
        
        # Get initial queryset
        queryset = Loan.objects.all()
        print(f"Initial queryset count: {queryset.count()}")
        print("Initial loans:", [
            f"ID: {loan.id}, Status: {loan.status}, User: {loan.user.username}"
            for loan in queryset
        ])

        # If user is not staff, apply visibility filter
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(user=self.request.user) |  # User's own loans
                Q(status__in=['pending', 'active'])  # Available and active loans
            )
            print(f"After visibility filter count: {queryset.count()}")
            print("Visible loans:", [
                f"ID: {loan.id}, Status: {loan.status}, User: {loan.user.username}"
                for loan in queryset
            ])

        # Get filter parameters
        status = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        print(f"Status filter: {status}")
        print(f"Search filter: {search}")

        # Apply status filter
        if status and status.lower() != 'all':
            status_mapping = {
                'Available': 'pending',
                'Funding': 'active',
                'Funded': 'completed'
            }
            backend_status = status_mapping.get(status)
            if backend_status:
                queryset = queryset.filter(status=backend_status)
                print(f"After status filter count: {queryset.count()}")

        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(purpose__icontains=search) |
                Q(description__icontains=search) |
                Q(user__username__icontains=search)
            )
            print(f"After search filter count: {queryset.count()}")

        # Final result
        final_queryset = queryset.order_by('-created_at')
        print(f"Final queryset count: {final_queryset.count()}")
        print("Final loans:", [
            f"ID: {loan.id}, Status: {loan.status}, User: {loan.user.username}"
            for loan in final_queryset
        ])
        print("=== End Debug Info ===\n")
        
        return final_queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Map backend statuses to frontend statuses
        status_mapping = {
            'pending': 'Available',
            'active': 'Funding',
            'completed': 'Funded'
        }
        
        data = serializer.data
        for loan in data:
            loan['status'] = status_mapping.get(loan['status'], loan['status'])
        
        print("Final Response Data:", data)  # Debug print
        return Response(data)

    # ... rest of your viewset methods remain the same ...

class LoanTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LoanType.objects.all()
    serializer_class = LoanTypeSerializer
    permission_classes = [IsAuthenticated]