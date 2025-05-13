from financial_management.loggers.financial_logger import FinancialLogger
from financial_management.models import Wallet, Transaction, AuditSeverity, AuditAction, WalletLedger
from financial_management.serivces.base import BaseWalletService
from django.db import transaction as db_transaction


class WalletWithdrawService(BaseWalletService):
    def validate(self):
        wallet = Wallet.objects.get(user=self.user)
        if self.amount >= wallet.balance:
            raise ValueError("Insufficient balance in wallet")

    def execute(self):
        self.validate()
        wallet = Wallet.objects.select_for_update().get(user=self.user)
        with db_transaction.atomic():
            transaction = Transaction.objects.create(
                user=self.user,
                amount=self.amount,
                type=Transaction.WITHDRAW,
                status=Transaction.SUCCESS
            )

            WalletLedger.objects.create(
                wallet=wallet,
                transaction=transaction,
                amount=self.amount,
                is_credit=False,
                balance_before=wallet.balance,
                balance_after=wallet.balance - self.amount,
                description='برداشت توسط کاربر',
            )

            FinancialLogger.log(
                user=self.user,
                action=AuditAction.WITHDRAW_SUCCESS,
                severity=AuditSeverity.INFO,
                transaction=transaction,
                ip_address=self.kwargs.get("ip"),
                user_agent=self.kwargs.get("agent"),
                extra_info={"amount": str(self.amount)}
            )

            wallet.balance -= self.amount
            wallet.save()

            return transaction


class WalletWithdrawRequestService(BaseWalletService):
    def validate(self):
        wallet = Wallet.objects.get(user=self.user)
        if self.amount >= wallet.balance:
            raise ValueError("Insufficient balance in wallet")

    def execute(self):
        self.validate()
        with db_transaction.atomic():
            FinancialLogger.log(
                user=self.user,
                action=AuditAction.WITHDRAW_REQUESTED,
                severity=AuditSeverity.INFO,
                transaction=None,
                ip_address=self.kwargs.get("ip"),
                user_agent=self.kwargs.get("agent"),
                extra_info={"amount": str(self.amount)}
            )
            return 'request log registered'
