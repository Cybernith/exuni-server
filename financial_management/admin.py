from django.contrib import admin

from financial_management.models import Wallet, Transaction, WalletLedger, AuditAction, FinancialAuditLog, Payment, \
    AffiliateOrderPayment

admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(WalletLedger)
admin.site.register(FinancialAuditLog)
admin.site.register(Payment)
admin.site.register(AffiliateOrderPayment)
