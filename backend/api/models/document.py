from django.db import models
from .loan import Loan

class Document(models.Model):
    loan = models.ForeignKey(Loan, related_name='documents', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='loan_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.loan.user.username}'s loan document - {self.name}"

    class Meta:
        ordering = ['-uploaded_at']
        
    def get_file_extension(self):
        """Get the file extension from the file name."""
        return self.name.split('.')[-1].lower() if '.' in self.name else ''
    
    def is_image(self):
        """Check if the file is an image."""
        image_extensions = ['jpg', 'jpeg', 'png', 'gif']
        return self.get_file_extension() in image_extensions
    
    def is_pdf(self):
        """Check if the file is a PDF."""
        return self.get_file_extension() == 'pdf'
        
    def file_size(self):
        """Get the file size in bytes."""
        try:
            return self.file.size
        except:
            return 0
            
    def file_url(self):
        """Get the complete URL for the file."""
        try:
            return self.file.url
        except:
            return None