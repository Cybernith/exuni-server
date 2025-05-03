from django.db import transaction as db_transaction

from financial_management.loggers.financial_logger import FinancialLogger
from financial_management.models import Wallet, Transaction, WalletLedger, AuditAction, AuditSeverity


class WalletTransferService:
    def _init_(self, sender_user, receiver_user, amount, ip=None, agent=None):
        self.sender_user = sender_user
        self.receiver_user = receiver_user
        self.amount = amount
        self.ip = ip
        self.agent = agent

    def validate(self):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")

        sender_wallet = Wallet.objects.get(user=self.sender_user)
        if sender_wallet.balance < self.amount:
            raise ValueError("Insufficient balance in sender wallet")

        if self.sender_user == self.receiver_user:
            raise ValueError("Cannot transfer to the same wallet")

    def execute(self):
        self.validate()

        sender_wallet = Wallet.objects.select_for_update().get(user=self.sender_user)
        receiver_wallet = Wallet.objects.select_for_update().get(user=self.receiver_user)

        with db_transaction.atomic():
            transaction = Transaction.objects.create(
                user=self.sender_user,
                related_user=self.receiver_user,
                amount=self.amount,
                type=Transaction.TRANSFER,
                status=Transaction.SUCCESS
            )

            # دفتر کل برای فرستنده (برداشت)
            WalletLedger.objects.create(
                wallet=sender_wallet,
                transaction=transaction,
                amount=self.amount,
                is_credit=False,
                balance_before=sender_wallet.balance,
                balance_after=sender_wallet.balance - self.amount,
                description=f"Transfer to {self.receiver_user}"
            )

            # دفتر کل برای گیرنده (واریز)
            WalletLedger.objects.create(
                wallet=receiver_wallet,
                transaction=transaction,
                amount=self.amount,
                is_credit=True,
                balance_before=receiver_wallet.balance,
                balance_after=receiver_wallet.balance + self.amount,
                description=f"Transfer from {self.sender_user}"
            )

            # لاگ
            FinancialLogger.log(
                user=self.sender_user,
                action=AuditAction.TRANSFER,
                severity=AuditSeverity.INFO,
                transaction=transaction,
                ip_address=self.ip,
                user_agent=self.agent,
                extra_info={
                    "from_user": str(self.sender_user),
                    "to_user": str(self.receiver_user),
                    "amount": str(self.amount)
                }
            )

            sender_wallet.balance -= self.amount
            receiver_wallet.balance += self.amount
            sender_wallet.save()
            receiver_wallet.save()

            return transaction
