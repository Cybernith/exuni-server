from helpers.functions import add_separator
from helpers.sms import Sms


class SMSHandler:

    @staticmethod
    def _format_numbers(phones):
        if isinstance(phones, str):
            return [phones]
        elif isinstance(phones, list):
            return phones
        else:
            raise ValueError("Invalid phone numbers format")

    @staticmethod
    def send_order_confirmation(order):
        from shop.models import ShopOrder
        shop_order = ShopOrder.objects.get(id=order)
        detail = shop_order.shipment_address
        sms_lines = [
            "اکسونی EXUNI ",
            "{} {}  عزیز".format(detail.first_name or '', detail.last_name or ''),
            "سفارش شما با موفقیت در اکسونی ثبت شد!",
            "شماره پیگیری سفارش شما: {}".format(shop_order.exuni_tracking_code),
            "مبلغ سفارش: {} تومان".format(add_separator(shop_order.final_amount)),
            "سفارش در حال آماده‌سازی برای بسته‌بندی هوشمند است.",
            "با هم می‌مانیم، در کنار هم می‌درخشیم.",
            "exuni.ir"
        ]

        sms_text = "\n".join(sms_lines)
        Sms.send(phone=shop_order.customer.username, message=sms_text)

    @staticmethod
    def send_orders_packing_start(orders):
        from shop.models import ShopOrder
        shop_orders = ShopOrder.objects.filter(id__in=orders).select_related('shipment_address', 'packager')
        messages = []
        numbers = []
        for order in shop_orders:
            detail = order.shipment_address
            sms_lines = [
                "اکسونی EXUNI ",
                "{} {}  عزیز".format(detail.first_name or '', detail.last_name or ''),
                "اکسونی در حال بسته‌بندی و آماده‌سازی سفارش شماست!",
                "سفارش شما توسط {} با کد پیگیری {}".format(order.packager.name, order.exuni_tracking_code),
                "در صف بسته‌بندی قرار گرفت و به زودی به پست ارسال می‌شود",
                "صبر شما تضمین کیفیت ماست",
                "exuni.ir/profile/orders",
            ]
            sms_text = "\n".join(sms_lines)
            messages.append(sms_text)
            numbers.append(order.customer.username)
        Sms.send_like_to_like(numbers, messages)


    @staticmethod
    def send_orders_shipped(orders):
        from shop.models import ShopOrder
        shop_orders = ShopOrder.objects.filter(id__in=orders).select_related('shipment_address', 'packager')
        messages = []
        numbers = []
        for order in shop_orders:
            detail = order.shipment_address
            sms_lines = [
                "اکسونی EXUNI ",
                "{} {}  عزیز".format(detail.first_name or '', detail.last_name or ''),
                "سفارش شما در اکسونی به پست ارسال شد!",
                " کد رهگیری پست {}".format(order.post_tracking_code),
                "پیگیری تحویل",
                "https://tracking.post.ir/search.aspx?id={}".format(order.post_tracking_code),
                "این بسته، راز انتخاب توئه!",
            ]
            sms_text = "\n".join(sms_lines)
            messages.append(sms_text)
            numbers.append(order.customer.username)
        Sms.send_like_to_like(numbers, messages)
