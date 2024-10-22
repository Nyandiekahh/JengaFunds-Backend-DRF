from django.db import models
from django.contrib.auth.models import User
from .loan import Loan

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan = models.ForeignKey(Loan, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.user.username}'s {self.type} transaction"