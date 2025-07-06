from rest_framework.throttling import UserRateThrottle


class PaymentRateThrottle(UserRateThrottle):
    rate = '30/min'

