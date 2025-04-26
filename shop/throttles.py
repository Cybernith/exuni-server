from rest_framework.throttling import UserRateThrottle


class SyncAllDataThrottle(UserRateThrottle):
    scope = 'sync_all_data'
