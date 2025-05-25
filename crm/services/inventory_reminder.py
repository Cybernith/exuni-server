from helpers.sms import Sms
from server.settings import FRONT_URL


def notify_users_if_in_stock(product):
    if product.stock > 0:
        reminders = product.stockreminder_set.filter(notified=False).select_related('user')

        if reminders.exists():
            phones = [reminder.user.mobile_number for reminder in reminders]
            link = f'{FRONT_URL}/products/{product.id}'
            message = f'{product.name}  موجود شد! همین حالا از {link} خرید کن 🎯'
            try:
                Sms.bulk_send(phones=phones, message=message)
                reminders.update(notified=True)
            except Exception as e:
                print(f"[SMS Bulk Error] {e}")
