# views/transaction_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from ..models import Transaction
from ..serializers.transaction_serializer import TransactionSerializer
import requests
import base64
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_access_token(self):
        """Get M-Pesa access token"""
        try:
            consumer_key = settings.MPESA_CONFIG['CONSUMER_KEY']
            consumer_secret = settings.MPESA_CONFIG['CONSUMER_SECRET']
            auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
            
            logger.info(f"Getting access token with key: {consumer_key}")
            
            response = requests.get(auth_url, auth=(consumer_key, consumer_secret))
            
            if response.status_code != 200:
                logger.error(f"Auth Error Response: {response.text}")
                raise Exception(f"Authentication failed with status {response.status_code}")
                
            token_data = response.json()
            logger.info("Successfully got access token")
            return token_data['access_token']
            
        except Exception as e:
            logger.error(f"Access Token Error: {str(e)}")
            raise

    def generate_password(self):
        """Generate M-Pesa password"""
        try:
            shortcode = settings.MPESA_CONFIG['SHORTCODE']
            passkey = settings.MPESA_CONFIG['PASSKEY']
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            password_str = f"{shortcode}{passkey}{timestamp}"
            password = base64.b64encode(password_str.encode()).decode()
            
            logger.info(f"Generated password with shortcode: {shortcode}")
            return password, timestamp
            
        except Exception as e:
            logger.error(f"Password Generation Error: {str(e)}")
            raise

    @action(detail=False, methods=['post'])
    def initiate_mpesa_payment(self, request):
        """Initiate M-Pesa STK push"""
        try:
            # Log incoming request
            logger.info(f"Payment initiation request: {request.data}")
            
            # Validate request data
            phone_number = request.data.get('phone_number')
            amount = request.data.get('amount')
            
            if not phone_number or not amount:
                return Response({
                    'error': 'Phone number and amount are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get access token
            access_token = self.get_access_token()
            password, timestamp = self.generate_password()
            
            # Prepare STK push request
            payload = {
                'BusinessShortCode': settings.MPESA_CONFIG['SHORTCODE'],
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': int(float(amount)),
                'PartyA': phone_number,
                'PartyB': settings.MPESA_CONFIG['SHORTCODE'],
                'PhoneNumber': phone_number,
                'CallBackURL': f"{settings.MPESA_CONFIG['BASE_URL']}/api/mpesa/callback/",
                'AccountReference': 'JengaFunds',
                'TransactionDesc': 'Payment to Jenga Funds'
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            # Log the request we're about to make
            logger.info(f"Making STK push request with payload: {payload}")
            
            # Make the request
            stk_push_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
            response = requests.post(stk_push_url, json=payload, headers=headers)
            
            # Log the response
            logger.info(f"STK push response: Status {response.status_code}, Body: {response.text}")
            
            response.raise_for_status()
            response_data = response.json()

            return Response({
                'message': 'STK push initiated successfully',
                'transaction_details': response_data
            })

        except requests.exceptions.RequestException as e:
            logger.error(f"STK Push Error: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Error Response: {e.response.text}")
            return Response({
                'error': 'Failed to initiate payment',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"General Error: {str(e)}")
            return Response({
                'error': 'An error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)