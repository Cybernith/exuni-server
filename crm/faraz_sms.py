import requests
import random

from django.core.exceptions import ValidationError

from server.settings import FARAZ_SMS_API_KEY, FARAZ_SMS_LINE_NUMBER, IPPANEL_BASE_URL


class IPPanelSMSService:

    def __init__(self):
        self.headers = {
            "accept": "*/*",
            "apikey": FARAZ_SMS_API_KEY,
            "Content-Type": "application/json"
        }

    @staticmethod
    def generate_code(digits: int = 6) -> int:
        start = 10 ** (digits - 1)
        end = 10 ** digits - 1
        return random.randint(start, end)

    def send_otp(self, phone: str) -> int:
        otp_code = self.generate_code()
        url = f"{IPPANEL_BASE_URL}/sms/pattern/normal/send"
        payload = {
            "code": 'pensvrur5oduf3l',
            "sender": FARAZ_SMS_LINE_NUMBER,
            "recipient": phone,
            "variable": {
                "verification-code": otp_code
            }
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return otp_code

