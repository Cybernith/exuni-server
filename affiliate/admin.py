from django.contrib import admin

from affiliate.models import AffiliateFactor, AffiliateFactorItem, PaymentInvoice, PaymentInvoiceItem
admin.site.register(AffiliateFactor)
admin.site.register(AffiliateFactorItem)
admin.site.register(PaymentInvoice)
admin.site.register(PaymentInvoiceItem)
