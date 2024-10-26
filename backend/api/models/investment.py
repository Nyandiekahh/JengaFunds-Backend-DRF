from django.db import models
from django.contrib.auth.models import User
from .loan import Loan

class LoanInvestment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('card', 'Credit/Debit Card')
    ]
    
    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    loan = models.ForeignKey(Loan, related_name='investments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.investor.username}'s investment of {self.amount} in loan #{self.loan.id}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Check if this is a new instance
        super().save(*args, **kwargs)
        
        if is_new or self.status == 'completed':
            # Update loan progress and status
            total_invested = self.loan.investments.filter(
                status='completed'
            ).aggregate(models.Sum('amount'))['amount__sum'] or 0
            
            self.loan.progress = (total_invested / float(self.loan.amount)) * 100
            
            if self.loan.progress >= 100:
                self.loan.status = 'Funded'
            elif self.loan.progress > 0:
                self.loan.status = 'Funding'
                
            self.loan.save()