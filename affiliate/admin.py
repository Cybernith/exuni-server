from django.contrib import admin

from affiliate.models import AffiliateFactor, AffiliateFactorItem, PaymentInvoice, PaymentInvoiceItem, Wallet, \
    Transaction

admin.site.register(AffiliateFactor)
admin.site.register(AffiliateFactorItem)
admin.site.register(PaymentInvoice)
admin.site.register(PaymentInvoiceItem)
admin.site.register(Wallet)
admin.site.register(Transaction)
