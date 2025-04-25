from crm.models import SearchLog, ShopProductViewLog


def save_search_log(request, query_value):
    if not request.session.session_key:
        request.session.save()
    SearchLog.objects.create(
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        user=request.user,
        query_value=query_value,
        ip_address=request.META.get("REMOTE_ADDR", ""),
        session_key=request.session.session_key,
    )


def save_product_view_log(request, product, referer=''):
    if not request.session.session_key:
        request.session.save()
    ShopProductViewLog.objects.create(
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        user=request.user,
        product=product,
        referer=referer,
        ip_address=request.META.get("REMOTE_ADDR", ""),
        session_key=request.session.session_key,
    )

