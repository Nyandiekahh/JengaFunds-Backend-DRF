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
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.IntegerField()

    def __str__(self):
        return f"{self.user.username}'s {self.loan_type.name} loan"