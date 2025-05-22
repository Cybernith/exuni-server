from datetime import timedelta

from django.db.models import Count, Q

from crm.models import SearchLog, ShopProductViewLog
from django.core.cache import cache
import datetime
import time
from functools import wraps
from collections import OrderedDict

from helpers.functions import get_current_user
from products.models import Product, Category, Brand, Avail, ProductProperty


def save_search_log(request, query_value, search_type=SearchLog.RAW_TEXT):
    if request.user.is_authenticated:
        user_key = f"user:{request.user.id}"
    else:
        if not request.session.session_key:
            request.session.save()
        user_key = f"anon:{request.session.session_key}"

    cache_key = f"search_log:{user_key}:{query_value}:{search_type}"
    if cache.get(cache_key):
        return

    # Ensure session exists
    if not request.session.session_key:
        request.session.save()

    log_kwargs = {
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        "user": request.user if request.user.is_authenticated else None,
        "query_value": query_value,
        "ip_address": request.META.get("REMOTE_ADDR", ""),
        "session_key": request.session.session_key,
        "search_type": search_type,
    }

    try:
        if search_type == SearchLog.PRODUCT:
            log_kwargs["product"] = Product.objects.filter(id=query_value).first()
        elif search_type == SearchLog.CATEGORY:
            log_kwargs["category"] = Category.objects.filter(id=query_value).first()
        elif search_type == SearchLog.BRAND:
            log_kwargs["brand"] = Brand.objects.filter(id=query_value).first()
        elif search_type == SearchLog.AVAIL:
            log_kwargs["avail"] = Avail.objects.filter(id=query_value).first()
        elif search_type == SearchLog.PROPERTY:
            log_kwargs["property"] = ProductProperty.objects.filter(id=query_value).first()
    except Exception as exception:
        pass

    SearchLog.objects.create(**log_kwargs)
    cache.set(cache_key, True, timeout=5 * 60)


def save_product_view_log(request, product):
    if request.user.is_authenticated:
        user_key = f"user:{get_current_user().id or request.session.session_key}"
    else:
        if not request.session.session_key:
            request.session.save()
        user_key = f"anon:{request.session.session_key}"

    cache_key = f"viewed:{user_key}:product:{product.id}"

    if cache.get(cache_key):
        return

    ShopProductViewLog.objects.create(
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        user=get_current_user() or None,
        product=product,
        ip_address=request.META.get("REMOTE_ADDR", ""),
        session_key=request.session.session_key,
        referer=request.META.get('HTTP_REFERER', "")
    )

    cache.set(cache_key, True, timeout=3600)


def get_user_interested(user, max_searches=20, max_visits=20, days=30):
    now = datetime.datetime.now()

    searches = (SearchLog.objects
                .filter(user=user, created_at__gte=now - timedelta(days=30))
                .order_by('-created_at')[:max_searches]).only('query_value')
    search_keywords = [search.query_value for search in searches]

    visits = (ShopProductViewLog.objects.filter(
        user=user, created_at__gte=now - timedelta(days)
    ).values('product').annotate(count=Count('id')).order_by('-count')[:max_visits])

    visited_product_ids = [visit['product'] for visit in visits]

    return search_keywords, visited_product_ids


def advanced_ttl_cache(timeout=300, maxsize=1000):
    cache_data = OrderedDict()

    def decorator(func):
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            user_id = user.id
            now = time.time()

            expired_keys = []
            for key, (_, timestamp) in cache_data.items():
                if now - timestamp > timeout:
                    expired_keys.append(key)
            for key in expired_keys:
                cache_data.pop(key, None)

            if user_id in cache_data:
                result, timestamp = cache_data[user_id]
                if now - timestamp < timeout:
                    cache_data.move_to_end(user_id)
                    return result

            result = func(user, *args, **kwargs)
            cache_data[user_id] = (result, now)
            cache_data.move_to_end(user_id)

            if len(cache_data) > maxsize:
                cache_data.popitem(last=False)

            return result
        return wrapper
    return decorator


@advanced_ttl_cache(timeout=300, maxsize=5000)
def get_recommended_products(user, limit=20):
    search_keywords, most_viewed_products_ids = get_user_interested(user)

    query = Q()
    for keyword in search_keywords:
        query |= Q(name__icontains=keyword) | Q(brand__name__icontains=keyword) | Q(category__name__icontains=keyword)

    related_products_by_search = Product.objects.filter(query).select_related('brand').only('id', 'name', 'brand__name')

    most_viewed_products = Product.objects.filter(
        id__in=most_viewed_products_ids
    ).select_related('brand').only('id', 'name', 'brand__name')

    all_products = (related_products_by_search | most_viewed_products).distinct()

    products_with_score = []
    for product in all_products:
        score = 0
        if any(keyword.lower() in product.name.lower() for keyword in search_keywords):
            score += 10
        if product.brand and any(keyword.lower() in product.brand.name.lower() for keyword in search_keywords):
            score += 8
        if product.category and any(keyword.lower() in product.category.name.lower() for keyword in search_keywords):
            score += 6
        if product.id in most_viewed_products_ids:
            score += 5
        products_with_score.append((product, score))

    products_with_score.sort(key=lambda x: x[1], reverse=True)

    return [product for product, score in products_with_score][:limit]
