from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class CMSUserRateThrottle(UserRateThrottle):
    rate = '10/min'


class CMSAnonRateThrottle(AnonRateThrottle):
    rate = '6/min'



