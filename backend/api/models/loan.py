from django.db import models
from django.contrib.auth.models import User

class LoanType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.IntegerField()

    def __str__(self):
        return self.name

class Loan(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Funding', 'Funding'),
        ('Funded', 'Funded')
    ]
    
    RISK_LEVEL_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    ]
    
    # ... rest of your model fields ...
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.IntegerField()
    purpose = models.CharField(max_length=255, default='General Purpose')  # Added with default
    description = models.TextField(default='Loan description not provided')  # Added with default
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, default='Medium')
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s loan - {self.amount}"

    @property
    def monthly_payment(self):
        total_interest = float(self.amount) * (float(self.interest_rate) / 100) * (self.term_months / 12)
        total_amount = float(self.amount) + total_interest
        return round(total_amount / self.term_months, 2)

    @property
    def total_return(self):
        total_interest = float(self.amount) * (float(self.interest_rate) / 100) * (self.term_months / 12)
        return round(float(self.amount) + total_interest, 2)