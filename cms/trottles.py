from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class CMSUserRateThrottle(UserRateThrottle):
    rate = '60/min'


class CMSAnonRateThrottle(AnonRateThrottle):
    rate = '30/min'



