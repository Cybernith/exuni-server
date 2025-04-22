from urllib.parse import urljoin

import requests

from server.settings import ZARINPAL_MERCHANT_ID


class ZarinpalGateway:
    GATEWAY_BASE_URL = 'https://api.zarinpal.com/pg/v4/payment'
    MERCHANT_ID = ZARINPAL_MERCHANT_ID

    def __init__(self, amount, description, callback_url, email=None, mobile=None):
        self.amount = amount
        self.description = description
        self.callback_url = callback_url
        self.email = email
        self.mobile = mobile

    def request_payment(self):
        data = {
            'merchant_id': self.MERCHANT_ID,
            'amount': self.amount,
            'callback_url': self.callback_url,
            'description': self.description,
        }
        if self.email:
            data['metadata'] = {'email': self.email}
        if self.mobile:
            data['metadata'] = data.get('metadata', {})
            data['metadata']['mobile'] = self.mobile

        response = requests.post(f"{self.GATEWAY_BASE_URL}/request.json", json=data)
        res_data = response.json()
        if res_data.get('data') and res_data['data'].get('code') == 100:
            authority = res_data['data']['authority']
            return {
                'authority': authority,
                'payment_url': f"https://api.zarinpal.com/pg/StartPay/{authority}"
            }
        else:
            error_message = str(res_data.get('errors'))
            Exception(f"zarinpal payment request failed: {error_message}")

    def verify_payment(self, authority):
        data = {
            'merchant_id': self.MERCHANT_ID,
            'amount': self.amount,
            'authority': authority,
        }
        response = requests.post(f"{self.GATEWAY_BASE_URL}/verify.json", json=data)
        return response.json()


