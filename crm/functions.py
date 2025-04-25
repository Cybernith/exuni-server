from crm.models import SearchLog, ShopProductViewLog
from django.core.cache import cache


def save_search_log(request, query_value, search_type=SearchLog.RAW_TEXT):
    if request.user.is_authenticated:
        user_key = f"user:{request.user.id}"
    else:
        if not request.session.session_key:
            request.session.save()
        user_key = f"anon:{request.session.session_key}"

    cache_key = f"search_log:{user_key}:{query_value}"
    if cache.get(cache_key):
        return

    if not request.session.session_key:
        request.session.save()
    SearchLog.objects.create(
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        user=request.user,
        query_value=query_value,
        ip_address=request.META.get("REMOTE_ADDR", ""),
        session_key=request.session.session_key,
        search_type=search_type
    )
    cache.set(cache_key, True, timeout=5 * 60)


def save_product_view_log(request, product):
    if request.user.is_authenticated:
        user_key = f"user:{request.user.id}"
    else:
        if not request.session.session_key:
            request.session.save()
        user_key = f"anon:{request.session.session_key}"

    cache_key = f"viewed:{user_key}:product:{product.id}"

    if cache.get(cache_key):
        return

    ShopProductViewLog.objects.create(
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        user=request.user,
        product=product,
        ip_address=request.META.get("REMOTE_ADDR", ""),
        session_key=request.session.session_key,
        referer=request.META.get('HTTP_REFERER', "")
    )

    cache.set(cache_key, True, timeout=3600)

