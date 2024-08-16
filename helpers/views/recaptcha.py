import json
from rest_framework.exceptions import ValidationError
from urllib.parse import urlencode
from urllib.request import urlopen

from server.settings import RECAPTCHA_PRIVATE_KEY, DEVELOPING


class RecaptchaView:
    """
    Adds `verify_recaptcha` method to the view to heck if recaptcha is valid
    """

    def verify_recaptcha(self):
        # disable recaptcha because of internet problems
        return True

        if DEVELOPING:
            return True

        URIReCaptcha = 'https://www.google.com/recaptcha/api/siteverify'
        recaptcha_response = self.request.data.get('recaptchaResponse', None)
        params = urlencode({
            'secret': RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response,
            'remote_ip': self.request.META.get('REMOTE_ADDR')
        })

        recaptcha_data = urlopen(URIReCaptcha, params.encode('utf-8')).read()
        result = json.loads(recaptcha_data)
        success = result.get('success', None)

        if not success:
            raise ValidationError('من ربات نیستم را تایید نمایید')
        return True
