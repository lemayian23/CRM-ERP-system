import os
import requests
import base64
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class MpesaClient:
    def __init__(self):
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
        self.shortcode = os.getenv('MPESA_SHORTCODE')
        self.passkey = os.getenv('MPESA_PASSKEY')
        self.callback_url = os.getenv('MPESA_CALLBACK_URL')
        self.environment = os.getenv('MPESA_ENVIRONMENT', 'sandbox')

        if self.environment == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'

        self.token_url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        self.stk_push_url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'

    def get_access_token(self):
        auth_str = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()
        headers = {'Authorization': f'Basic {encoded_auth}'}
        response = requests.get(self.token_url, headers=headers)
        if response.status_code == 200:
            return response.json().get('access_token')
        raise Exception(f"Token error: {response.text}")

    def generate_password(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        encoded_password = base64.b64encode(password_str.encode()).decode()
        return encoded_password, timestamp

    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        # Format phone number to 254XXXXXXXXX
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+'):
            phone_number = phone_number[1:]

        access_token = self.get_access_token()
        password, timestamp = self.generate_password()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone_number,
            'PartyB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': self.callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }

        response = requests.post(self.stk_push_url, json=payload, headers=headers)
        return response.json()