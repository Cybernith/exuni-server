from django.utils.timezone import now


class DiscountEngine:
    def __init__(self, order, user=None):
        self.order = order
        self.user = user

    def get_applicable_rules(self):
        rules = DiscountRule.objects.filter(is_active=True, start_at__lte=now(), end_at__gte=now())
        return [rule for rule in rules if self.evaluate(rule.conditions)]

    def evaluate(self, conditions):
        # مثال شرط: {"brands": [1, 2], "min_total_price": 300000, "shipping_city": "تهران"}
        # باید با داده‌های سفارش match بشه
        ...