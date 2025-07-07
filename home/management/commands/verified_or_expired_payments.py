from django.core.management import BaseCommand
from django.db.models import Q

from financial_management.loggers.financial_logger import FinancialLogger
from financial_management.models import Payment, AuditAction, AuditSeverity, Transaction
from financial_management.serivces.wallet_top_up_service import WalletTopUpService
from financial_management.zarinpal import ZarinpalGateway
from helpers.functions import datetime_to_str
from shop.models import ShopOrder
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'expired pending orders'

    def handle(self, *args, **options):
        print(f' expired pending orders cron job run in {datetime_to_str(datetime.now())}')
        datetime_check = datetime.now() - timedelta(minutes=15)
        for payment in Payment.objects.filter(Q(status=Payment.PENDING) & Q(created_at__lt=datetime_check)):
            if payment.type == Payment.FOR_SHOP_ORDER and payment.shop_order:
                order = payment.shop_order
                gateway = ZarinpalGateway(
                    amount=payment.amount,
                    description=f'تایید پرداخت سفارش {order.id} کاربر {order.customer.mobile_number}',
                    callback_url=''
                )
                result = gateway.verify_payment(payment.reference_id)
                if result.get('data') and result['data'].get('code') in [100, 101]:
                    if payment.used_amount_from_wallet > 0:
                        wallet = payment.user.exuni_wallet

                        wallet.reduce_balance(
                            transaction_id=payment.transaction_id,
                            amount=payment.used_amount_from_wallet,
                            shop_order=order,
                            description=f"پرداخت قسمتی از مبلغ سفارش {order.id}"
                        )
                        FinancialLogger.log(
                            user=order.customer,
                            action=AuditAction.PAYMENT_ORDER_FROM_WALLET,
                            severity=AuditSeverity.INFO,
                            transaction=Transaction.objects.get(transaction_id=payment.transaction_id),
                            extra_info={
                                "amount": str(payment.used_amount_from_wallet),
                                "order": str(order.id),
                            }
                        )

                        wallet.refresh_from_db()
                    payment.zarinpal_ref_id = result['data'].get('ref_id')
                    payment.card_pan = result['data'].get('card_pan')
                    payment.fee = result['data'].get('fee')
                    payment.is_verified = True
                    payment.save()
                    payment.mark_as_success_payment(user=payment.user)
                    FinancialLogger.log(
                        user=payment.user,
                        action=AuditAction.PAYMENT_ORDER,
                        severity=AuditSeverity.INFO,
                        payment=payment,
                        extra_info={
                            "amount": str(payment.amount),
                            "order": str(order.id),
                            "authority": payment.reference_id,
                        }
                    )

                    if order.discount_code:
                        order.discount_code.use()
                    if order.status == ShopOrder.PENDING:
                        order.mark_as_paid()

                else:
                    payment.mark_as_expired_payment()

            if payment.type == Payment.FOR_TOP_UP_WALLET:
                gateway = ZarinpalGateway(
                    amount=payment.amount,
                    description=f'شارژ کیف پول {payment.user}',
                    callback_url=''
                )

                result = gateway.verify_payment(payment.reference_id)

                if result.get('data') and result['data'].get('code') in [100, 101]:
                    payment.zarinpal_ref_id = result['data'].get('ref_id')
                    payment.card_pan = result['data'].get('card_pan')
                    payment.fee = result['data'].get('fee')
                    payment.save()
                    payment.mark_as_success_payment(user=payment.user)
                    FinancialLogger.log(
                        user=payment.user,
                        action=AuditAction.PAYMENT_FOR_TOP_UP_WALLET,
                        severity=AuditSeverity.INFO,
                        payment=payment,
                        extra_info={"amount": str(payment.amount)}
                    )

                    service = WalletTopUpService(
                        user=payment.user,
                        amount=payment.amount,
                        transaction_id=payment.transaction_id,
                    )

                    try:
                        service.execute()
                    except Exception as e:
                        pass
                else:
                    payment.mark_as_expired_payment()


