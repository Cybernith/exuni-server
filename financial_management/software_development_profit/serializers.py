from django.db.models import Sum, ExpressionWrapper, F, DecimalField, Q
from rest_framework.fields import FloatField

from helpers.models import DECIMAL
from shop.models import ShopOrder
from rest_framework import serializers

from users.serializers import UserSimpleSerializer


class SoftwareDevelopmentShopOrderSimpleSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    payment_display = serializers.ReadOnlyField()
    amount_sum = serializers.SerializerMethodField()

    class Meta:
        model = ShopOrder
        fields = '__all__'

    def get_amount_sum(self, obj):
        currency_ids = [14, 15, 17]
        filtered_items = obj.items.filter(Q(product__currency_id__in=currency_ids) | Q(product__currency__isnull=True))
        return filtered_items.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('price') * F('product_quantity'),
                    output_field=DECIMAL()
                )
            )
        )['total'] or 0


