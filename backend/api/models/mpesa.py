# api/models/mpesa.py
from django.db import models
from django.contrib.auth.models import User

class MpesaTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    merchant_request_id = models.CharField(max_length=100, null=True)
    checkout_request_id = models.CharField(max_length=100, null=True)
    response_code = models.CharField(max_length=5, null=True)
    response_description = models.CharField(max_length=255, null=True)
    customer_message = models.CharField(max_length=255, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"M-Pesa transaction for {self.user.username} - {self.amount}"
