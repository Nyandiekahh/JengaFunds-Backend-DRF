from rest_framework import serializers
from ..models import Document

class DocumentSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 
            'name', 
            'file', 
            'uploaded_at', 
            'file_size',
            'file_type',
            'file_url'
        ]
        read_only_fields = ['uploaded_at', 'file_size', 'file_type']

    def get_file_size(self, obj):
        return obj.file_size()

    def get_file_type(self, obj):
        if obj.is_pdf():
            return 'pdf'
        elif obj.is_image():
            return 'image'
        return 'document'

    def get_file_url(self, obj):
        return obj.file_url()

    def validate_file(self, value):
        # Add file validation if needed
        max_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_size:
            raise serializers.ValidationError('File size cannot exceed 5MB')
            
        allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'docx', 'doc']
        ext = value.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                'Unsupported file format. Allowed formats: PDF, JPG, JPEG, PNG, DOCX, DOC'
            )
            
        return value