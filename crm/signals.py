
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from crm.models import SearchLog, ShopProductViewLog


@receiver(user_logged_in)
def connect_session_data(sender, user, request, **kwargs):
    session_key = request.session.session_key
    if not session_key:
        return

    SearchLog.objects.filter(user__isnull=True, session_key=session_key).update(user=user)
    ShopProductViewLog.objects.filter(user__isnull=True, session_key=session_key).update(user=user)
