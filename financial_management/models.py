from django.core.exceptions import ValidationError
from django.db import models


class Wallet(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='wallet',
                                blank=True, null=True)
    business = models.OneToOneField('main.Business', on_delete=models.CASCADE, related_name='wallet',
                                    blank=True, null=True)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if not self.user and not self.business:
            raise ValidationError("حداقل یکی از فیلدهای 'کاربر' یا 'کسب و کار' باید مقدار داشته باشد.")


class Transaction(models.Model):
    TOP_UP = 'top-up'
    WITHDRAW = 'withdraw'
    TRANSFER = 'transfer'
    PAYMENT = 'payment'
    INVESTMENT = 'investment'

    TRANSACTION_TYPE = (
        (TOP_UP, 'شارژ ولت'),
        (WITHDRAW, 'برداشت'),
        (TRANSFER, 'انتقال'),
        (PAYMENT, 'پرداخت'),
        (INVESTMENT, 'سرمایه گذاری'),
    )

    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'

    TRANSACTION_STATUS = (
        (PENDING, 'بلاتکلیف'),
        (SUCCESS, 'موفق'),
        (FAILED, 'ناموفق'),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default='PENDING')
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WalletLedger(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='ledgers')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)

    amount = models.DecimalField(max_digits=20, decimal_places=2)
    balance_before = models.DecimalField(max_digits=20, decimal_places=2)
    balance_after = models.DecimalField(max_digits=20, decimal_places=2)
    is_credit = models.BooleanField()

    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class BankAccount(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bank_accounts')
    business = models.ForeignKey('main.Business', on_delete=models.CASCADE, related_name='bank_accounts',
                                 blank=True, null=True)

    bank_name = models.CharField(max_length=100)
    iban = models.CharField(max_length=26)
    card_number = models.CharField(max_length=16)
    is_verified = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        if not self.user and not self.business:
            raise ValidationError("حداقل یکی از فیلدهای 'کاربر' یا 'کسب و کار' باید مقدار داشته باشد.")


class AuditAction(models.TextChoices):
    TOP_UP_REQUESTED = "wallet_top_up_requested", "Top-up Requested"
    TOP_UP_SUCCESS = "wallet_top_up_success", "Top-up Success"
    TRANSFER = "wallet_transfer", "Wallet Transfer"
    WITHDRAW = "wallet_withdrawal", "Wallet Withdrawal"
    PAYMENT_ORDER = "wallet_payment_order", "Payment for Order"
    INVESTMENT = "wallet_investment", "Investment Made"
    BALANCE_UPDATED = "wallet_balance_updated", "Balance Updated"
    TRANSACTION_FAILED = "transaction_failed", "Transaction Failed"
    MANUAL_ADJUSTMENT = "admin_manual_adjustment", "Manual Adjustment"


class AuditSeverity(models.TextChoices):
    INFO = "info", "Info"
    WARNING = "warning", "Warning"
    CRITICAL = "critical", "Critical"


class FinancialAuditLog(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='pay_logs')
    receiver = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='receive_logs')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=AuditAction.choices)
    severity = models.CharField(max_length=10, choices=AuditSeverity.choices, default=AuditSeverity.INFO)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=256)
    extra_info = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)