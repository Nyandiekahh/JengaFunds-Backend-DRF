# api/serializers/mpesa_serializer.py
from rest_framework import serializers
from ..models.mpesa import MpesaTransaction

class MpesaTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaTransaction
        fields = ['id', 'phone_number', 'amount', 'reference', 'description', 
                 'status', 'created_at', 'customer_message']
        read_only_fields = ['status', 'created_at', 'customer_message']
