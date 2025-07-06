from rest_framework.throttling import BaseThrottle, UserRateThrottle, AnonRateThrottle
from rest_framework.exceptions import Throttled
from django.core.cache import cache
import time

from users.models import User


class UserProductListRateThrottle(UserRateThrottle):
    rate = '60/min'


class AnonProductListRateThrottle(AnonRateThrottle):
    rate = '60/min'


class UserProductDetailRateThrottle(UserRateThrottle):
    rate = '60/min'


class AnonProductDetailRateThrottle(AnonRateThrottle):
    rate = '60/min'


class CreateCommentRateThrottle(UserRateThrottle):
    rate = '60/min'


class RateUpsertRateThrottle(UserRateThrottle):
    rate = '60/min'


class CategoryTreeThrottle(UserRateThrottle):
    rate = '60/min'

class RootCategoryThrottle(UserRateThrottle):
    rate = '60/min'

class BrandThrottle(UserRateThrottle):
    rate = '60/min'


class DynamicRateThrottle(BaseThrottle):
    def __init__(self):
        self.history = None

    rates = {
        'anon': {'GET': 30, 'POST': 10},
        'authenticated': {'GET': 60, 'POST': 20},
        'staff': {'GET': 120, 'POST': 60},
        'manager': {'GET': 180, 'POST': 90},
    }

    def get_cache_key(self, request):
        if request.user.is_authenticated:
            return f'throttle_user_{request.user.id}'
        else:
            return f'throttle_anon_{self.get_ident(request)}'

    def get_rate(self, request):
        method = request.method

        if request.user.is_authenticated:
            if getattr(request.user, 'user_type') and request.user.user_type == User.MANAGER:
                user_type = 'manager'
            elif request.user.is_staff:
                user_type = 'staff'
            else:
                user_type = 'authenticated'
        else:
            user_type = 'anon'

        return self.rates.get(user_type, {}).get(method, 10)

    def allow_request(self, request, view):
        cache_key = self.get_cache_key(request)
        rate = self.get_rate(request)

        self.history = cache.get(cache_key, [])
        now = time.time()

        self.history = [timestamp for timestamp in self.history if now - timestamp < 60]

        if len(self.history) >= rate:
            raise Throttled(detail=f"Throttle limit exceeded. Max {rate} {request.method} requests per minute.")

        self.history.append(now)
        cache.set(cache_key, self.history, timeout=60)

        return True

    def wait(self):
        if self.history:
            earliest = min(self.history)
            return 60 - (time.time() - earliest)
        return None