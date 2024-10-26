from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import mimetypes

from ..models.loan import Loan
from ..models.document import Document  # Add this import
from ..serializers.loan_serializer import LoanSerializer  # This should work now

class LoanDocumentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, loan_pk=None):
        try:
            loan = Loan.objects.get(id=loan_pk, user=request.user)
        except Loan.DoesNotExist:
            return Response(
                {'error': 'Loan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a unique filename
        filename = f"loan_{loan.id}_{file.name}"
        path = default_storage.save(f'loan_documents/{filename}', ContentFile(file.read()))

        # Save document reference in loan
        Document.objects.create(  # Use the Document model directly
            loan=loan,
            name=file.name,
            file=path
        )

        return Response({
            'status': 'success',
            'message': 'Document uploaded successfully',
            'file_name': file.name
        })

    def retrieve(self, request, pk=None, loan_pk=None):
        try:
            loan = Loan.objects.get(id=loan_pk)
            document = Document.objects.get(id=pk, loan=loan)  # Updated query
        except (Loan.DoesNotExist, Document.DoesNotExist):
            return Response(
                {'error': 'Document not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Check permissions
        if not (request.user == loan.user or 
                loan.investments.filter(investor=request.user).exists()):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Return file
        file_path = document.file.path
        if os.path.exists(file_path):
            content_type = mimetypes.guess_type(file_path)[0]
            with open(file_path, 'rb') as f:
                response = Response(
                    f.read(),
                    content_type=content_type
                )
                response['Content-Disposition'] = f'attachment; filename="{document.name}"'
                return response

        return Response(
            {'error': 'File not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )