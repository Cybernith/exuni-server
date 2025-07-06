from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class SyncAllDataThrottle(UserRateThrottle):
    scope = 'sync_all_data'


class UserSearchAutoCompleteRateThrottle(UserRateThrottle):
    rate = '60/min'


class AnonSearchAutoCompleteRateThrottle(AnonRateThrottle):
    rate = '60/min'


class AddToCardRateThrottle(UserRateThrottle):
    rate = '60/min'


class AddToWishListRateThrottle(UserRateThrottle):
    rate = '60/min'


class AddToComparisonRateThrottle(UserRateThrottle):
    rate = '60/min'


class ShopOrderRateThrottle(UserRateThrottle):
    rate = '60/min'


class ToggleWishListBtnRateThrottle(UserRateThrottle):
    rate = '60/min'


class ToggleComparisonBtnRateThrottle(UserRateThrottle):
    rate = '60/min'


class OrderRetrieveThrottle(UserRateThrottle):
    rate = '60/min'
