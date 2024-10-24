# api/views/mpesa_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import requests
import base64
from datetime import datetime
from ..models.mpesa import MpesaTransaction
from ..serializers.mpesa_serializer import MpesaTransactionSerializer
import os
from dotenv import load_dotenv

load_dotenv()

def get_access_token():
    consumer_key = os.getenv('MPESA_CONSUMER_KEY')
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
    auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    
    try:
        auth_response = requests.get(
            auth_url,
            auth=(consumer_key, consumer_secret)
        )
        auth_response.raise_for_status()
        return auth_response.json()['access_token']
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error getting access token: {str(e)}")

def generate_password():
    shortcode = os.getenv('MPESA_SHORTCODE')
    passkey = os.getenv('MPESA_PASSKEY')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    password_str = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(password_str.encode()).decode(), timestamp

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_stk_push(request):
    try:
        phone_number = request.data.get('phoneNumber')
        amount = request.data.get('amount')
        description = request.data.get('description', 'Payment to Jenga Funds')
        
        if not phone_number or not amount:
            return Response({
                'error': 'Phone number and amount are required'
            }, status=400)

        # Get M-Pesa access token
        access_token = get_access_token()
        password, timestamp = generate_password()
        
        payload = {
            'BusinessShortCode': os.getenv('MPESA_SHORTCODE'),
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(float(amount)),
            'PartyA': phone_number,
            'PartyB': os.getenv('MPESA_SHORTCODE'),
            'PhoneNumber': phone_number,
            'CallBackURL': f"{os.getenv('BASE_URL')}/api/mpesa/callback/",
            'AccountReference': 'JengaFunds',
            'TransactionDesc': description
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        
        response = requests.post(
            'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
            json=payload,
            headers=headers
        )
        
        response_data = response.json()
        
        # Create M-Pesa transaction record
        mpesa_transaction = MpesaTransaction.objects.create(
            user=request.user,
            phone_number=phone_number,
            amount=amount,
            reference=f"JF{timestamp}",
            description=description,
            merchant_request_id=response_data.get('MerchantRequestID'),
            checkout_request_id=response_data.get('CheckoutRequestID')
        )
        
        return Response({
            'message': 'STK push initiated successfully',
            'transaction_id': mpesa_transaction.id,
            'merchant_request_id': response_data.get('MerchantRequestID'),
            'checkout_request_id': response_data.get('CheckoutRequestID'),
            'response_code': response_data.get('ResponseCode'),
            'customer_message': response_data.get('CustomerMessage')
        })
        
    except Exception as e:
        return Response({
            'error': 'An error occurred',
            'details': str(e)
        }, status=500)

@api_view(['POST'])
def mpesa_callback(request):
    """Handle M-Pesa callback"""
    callback_data = request.data.get('Body', {}).get('stkCallback', {})
    merchant_request_id = callback_data.get('MerchantRequestID')
    checkout_request_id = callback_data.get('CheckoutRequestID')
    result_code = callback_data.get('ResultCode')
    result_desc = callback_data.get('ResultDesc')
    
    try:
        transaction = MpesaTransaction.objects.get(
            merchant_request_id=merchant_request_id,
            checkout_request_id=checkout_request_id
        )
        
        if result_code == 0:
            transaction.status = 'COMPLETED'
            # Create a regular transaction record
            Transaction.objects.create(
                user=transaction.user,
                type='credit',
                amount=transaction.amount,
                description=f"M-Pesa payment: {transaction.reference}",
            )
        else:
            transaction.status = 'FAILED'
            
        transaction.response_code = str(result_code)
        transaction.response_description = result_desc
        transaction.customer_message = result_desc
        transaction.save()
        
        return Response({'message': 'Callback processed successfully'})
        
    except MpesaTransaction.DoesNotExist:
        return Response({
            'error': 'Transaction not found'
        }, status=404)
    except Exception as e:
        return Response({
            'error': 'Error processing callback',
            'details': str(e)
        }, status=500)
