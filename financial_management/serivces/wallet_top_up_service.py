from financial_management.loggers.financial_logger import FinancialLogger
from financial_management.models import Wallet, Transaction, AuditSeverity, AuditAction, WalletLedger
from financial_management.serivces.base import BaseWalletService
from django.db import transaction as db_transaction


class WalletTopUpService(BaseWalletService):
    def validate(self):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")

    def execute(self):
        self.validate()
        wallet = Wallet.objects.select_for_update().get(user=self.user)
        with db_transaction.atomic():
            transaction = Transaction.objects.create(
                wallet=wallet,
                amount=self.amount,
                type=Transaction.TOP_UP,
                status=Transaction.SUCCESS
            )

            WalletLedger.objects.create(
                wallet=wallet,
                transaction=transaction,
                amount=self.amount,
                is_credit=True,
                balance_before=wallet.balance,
                balance_after=wallet.balance + self.amount,
                description='شارژ توسط کاربر',
            )

            FinancialLogger.log(
                user=self.user,
                action=AuditAction.TOP_UP_SUCCESS,
                severity=AuditSeverity.INFO,
                transaction=transaction,
                ip_address=self.ip,
                user_agent=self.agent,
                extra_info={"amount": str(self.amount)}
            )

            wallet.increase_balance(self.amount)
            return transaction


class WalletTopUpRequestService(BaseWalletService):
    def validate(self):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")

    def execute(self):
        self.validate()
        with db_transaction.atomic():
            FinancialLogger.log(
                user=self.user,
                action=AuditAction.TOP_UP_REQUESTED,
                severity=AuditSeverity.INFO,
                transaction=None,
                ip_address=self.ip,
                user_agent=self.agent,
                extra_info={"amount": str(self.amount)}
            )
            return 'request log registered'
