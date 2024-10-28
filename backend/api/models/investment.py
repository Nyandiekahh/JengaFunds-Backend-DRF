from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
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
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new or self.status == 'completed':
            # Update loan progress and status
            total_invested = self.loan.investments.filter(
                status='completed'
            ).aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0')
            
            # Convert to Decimal for calculation
            loan_amount = self.loan.amount
            if total_invested and loan_amount:
                progress = (total_invested / loan_amount * Decimal('100')).quantize(Decimal('0.01'))
            else:
                progress = Decimal('0.00')
            
            self.loan.progress = progress
            
            # Update loan status based on progress
            if progress >= Decimal('100.00'):
                self.loan.status = 'Funded'
            elif progress > Decimal('0.00'):
                self.loan.status = 'Funding'
            
            self.loan.save()

    @property
    def return_amount(self):
        """Calculate the expected return amount including interest"""
        if self.status != 'completed' or not self.loan.interest_rate:
            return Decimal('0.00')
        
        interest_rate = self.loan.interest_rate / Decimal('100')
        term_years = Decimal(str(self.loan.term_months)) / Decimal('12')
        return self.amount + (self.amount * interest_rate * term_years)

    @property
    def return_rate(self):
        """Get the return rate for this investment"""
        return self.loan.interest_rate if self.loan else Decimal('0.00')

    @property
    def is_active(self):
        """Check if investment is active"""
        return self.status == 'completed' and self.loan.status in ['Funding', 'Funded']