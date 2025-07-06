from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class UserFinalSearchLogRateThrottle(UserRateThrottle):
    rate = '60/min'


class AnonFinalSearchLogRateThrottle(AnonRateThrottle):
    rate = '60/min'
