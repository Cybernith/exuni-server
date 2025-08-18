# services/payment_service.py
from django.db import transaction
from django.urls import reverse
from django.conf import settings

from financial_management.loggers.financial_logger import FinancialLogger
from financial_management.models import AuditAction, AuditSeverity, Transaction

import random
import string

from financial_management.zarinpal import ZarinpalGateway
from helpers.functions import date_to_str
from shop.models import ShopOrder


def generate_payment_code_with_mobile(mobile_number):
    prefix = "PFW"
    random_chars_len = 20 - len(prefix) - len(mobile_number)
    random_chars = ''.join(random.choices(string.ascii_uppercase, k=random_chars_len))
    return prefix + mobile_number + random_chars


class PaymentService:

    @staticmethod
    @transaction.atomic
    def start_payment(order, use_wallet=False, ip=None, agent=None):
        payment = getattr(order, "bank_payment", None)
        if payment and payment.status == "su":
            raise ValueError("این سفارش قبلاً پرداخت موفق داشته است.")
        elif payment and payment.status != "su":
            payment.delete()
            order.bank_payment = None
            order.save()

        if use_wallet:
            transaction_id = generate_payment_code_with_mobile(order.customer.mobile_number)
            payment = order.pay_with_wallet(transaction_id=transaction_id)

            if not payment:
                FinancialLogger.log(
                    user=order.customer,
                    action=AuditAction.PAYMENT_ORDER_FROM_WALLET,
                    severity=AuditSeverity.INFO,
                    transaction=Transaction.objects.get(transaction_id=transaction_id),
                    ip_address=ip,
                    user_agent=agent,
                    extra_info={"amount": str(order.final_amount), "order": str(order.id)},
                )
                return {
                    "payment_url": f"/payment/success?status=success&type=wallet&payment_date={date_to_str(order.date_time)}&amount={order.final_amount}&order_id={order.id}"
                }

        else:
            payment = order.pay()

        callback_url = settings.SERVER_URL + reverse("financial_management:zarinpal_callback")
        description = f"پرداخت سفارش {order.id} کاربر {order.customer.mobile_number}"
        if use_wallet:
            description += f" مبلغ {payment.used_amount_from_wallet} از کیف پول"

        gateway = ZarinpalGateway(
            amount=payment.amount,
            mobile=payment.shop_order.customer.mobile_number,
            payment_id=order.id,
            description=description,
            callback_url=callback_url,
        )

        result = gateway.request_payment()
        payment.reference_id = result["authority"]
        payment.save()

        FinancialLogger.log(
            user=payment.user,
            action=AuditAction.PAYMENT_REQUEST,
            severity=AuditSeverity.INFO,
            payment=payment,
            ip_address=ip,
            user_agent=agent,
            extra_info={
                "amount": str(payment.amount),
                "authority": result["authority"],
                "order": str(order.id),
                "used_from_wallet": str(payment.used_amount_from_wallet),
            },
        )

        return {"payment_url": result["payment_url"]}
