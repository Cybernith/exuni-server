from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class UserFinalSearchLogRateThrottle(UserRateThrottle):
    rate = '50/min'


class AnonFinalSearchLogRateThrottle(AnonRateThrottle):
    rate = '30/min'
