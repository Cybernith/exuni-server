import requests

from server.gateway_configs import ZARINPAL_MERCHANT_ID, GATEWAY_BASE_URL, GATEWAY_START_PAY_URL, \
    GATEWAY_DEVELOPMENT_URL, GATEWAY_DEVELOPMENT_START_PAY_URL


class ZarinpalGateway:
    GATEWAY_BASE_URL = GATEWAY_DEVELOPMENT_URL
    MERCHANT_ID = ZARINPAL_MERCHANT_ID
    GATEWAY_START_PAY_URL = GATEWAY_DEVELOPMENT_START_PAY_URL

    def __init__(self, amount, description, callback_url, payment_id=None, email=None, mobile=None):
        self.amount = amount
        self.description = description
        self.callback_url = callback_url
        self.email = email
        self.mobile = mobile
        self.payment_id = payment_id

    def request_payment(self):
        data = {
            'merchant_id': self.MERCHANT_ID,
            'amount': self.amount,
            'currency': 'IRR',
            'callback_url': self.callback_url,
            'description': self.description,
            'order_id': self.payment_id,
        }
        if self.email:
            data['metadata'] = {'email': self.email}
        if self.mobile:
            data['metadata'] = data.get('metadata', {})
            data['metadata']['mobile'] = self.mobile

        response = requests.post(f"{self.GATEWAY_BASE_URL}/request.json", json=data)
        res_data = response.json()

        if res_data['data'] and res_data['data']['code'] == 100 and \
                res_data['data']['authority'].startswith('S'):
            authority = res_data['data']['authority']
            return {
                'authority': authority,
                'payment_url': f"{self.GATEWAY_START_PAY_URL}/{authority}"
            }
        else:
            error_message = str(res_data['error'])
            Exception(f"zarinpal payment request failed: {error_message}")

    def verify_payment(self, authority):
        data = {
            'merchant_id': self.MERCHANT_ID,
            'amount': self.amount,
            'authority': authority,
        }
        response = requests.post(f"{self.GATEWAY_BASE_URL}/verify.json", json=data)
        return response.json()


