from rest_framework.throttling import UserRateThrottle


class PaymentRateThrottle(UserRateThrottle):
    rate = '10/hour'

