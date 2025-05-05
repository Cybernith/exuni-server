from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class SyncAllDataThrottle(UserRateThrottle):
    scope = 'sync_all_data'


class UserSearchAutoCompleteRateThrottle(UserRateThrottle):
    rate = '60/min'


class AnonSearchAutoCompleteRateThrottle(AnonRateThrottle):
    rate = '40/min'


class AddToCardRateThrottle(UserRateThrottle):
    rate = '20/min'


class AddToWishListRateThrottle(UserRateThrottle):
    rate = '30/min'


class AddToComparisonRateThrottle(UserRateThrottle):
    rate = '30/min'


class ShopOrderRateThrottle(UserRateThrottle):
    rate = '6/hour'
