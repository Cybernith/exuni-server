from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class UserChatGPTThrottle(UserRateThrottle):
    rate = '5/min'


class AnonChatGPTThrottle(AnonRateThrottle):
    rate = '100/day'


class DeleteSearchHistoryRateThrottle(UserRateThrottle):
    rate = '3/min'
