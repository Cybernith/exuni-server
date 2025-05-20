from django.db.models.signals import pre_save
from django.dispatch import receiver
from shop.models import ShopOrder, ShopOrderStatusHistory

@receiver(pre_save, sender=ShopOrder)
def log_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        previous = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if previous.status != instance.status:
        ShopOrderStatusHistory.objects.create(
            shop_order=instance,
            previous_status=previous.status,
            new_status=instance.status,
            changed_by=getattr(instance, "_status_changed_by", None),
            note=f"وضعیت سفارش از {previous.status} به {instance.status} تغییر کرد."
        )
