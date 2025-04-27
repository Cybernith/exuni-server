from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class UserUpdateRateThrottle(UserRateThrottle):
    rate = '6/hour'


class UserCreateRateThrottle(AnonRateThrottle):
    rate = '6/min'


