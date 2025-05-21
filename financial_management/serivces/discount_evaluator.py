from decimal import Decimal

from financial_management.models import DiscountCondition


def evaluate_discount(discount, cart_items, user, total_price):
    if not discount.is_valid():
        return None

    valid = True
    reasons = []

    for condition in discount.conditions.all():
        if condition.type == DiscountCondition.CATEGORY:
            allowed_cats = condition.category_condition.categories.all()
            if not any(item['product'].category in allowed_cats for item in cart_items):
                valid = False
                reasons.append("محصولات در دسته‌بندی مجاز نیست.")

        elif condition.type == DiscountCondition.PRODUCT:
            allowed_products = condition.product_condition.products.all()
            if not any(item['product'] in allowed_products for item in cart_items):
                valid = False
                reasons.append("محصولات سبد با شرط تطابق ندارند.")

        elif condition.type == DiscountCondition.BRAND:
            allowed_brands = condition.brand_condition.brands.all()
            if not any(item['product'].brand in allowed_brands for item in cart_items):
                valid = False
                reasons.append("محصولات از برند مجاز نیست.")

        elif condition.type == DiscountCondition.USER:
            allowed_users = condition.user_condition.users.all()
            if user not in allowed_users:
                valid = False
                reasons.append("این تخفیف برای کاربر شما نیست.")

        elif condition.type == DiscountCondition.PRICE_OVER:
            if total_price < condition.price_over_condition.price_over:
                valid = False
                reasons.append(f"قیمت سفارش کمتر از {condition.price_over_condition.price_over} است.")

        elif condition.type == DiscountCondition.PRICE_LIMIT:
            if total_price > condition.price_limit_condition.price_limit:
                valid = False
                reasons.append(f"قیمت سفارش بیشتر از {condition.price_limit_condition.price_limit} است.")

    if not valid:
        return None

    action = discount.action
    discount_value = Decimal("0.00")

    if action.type == action.PERCENTAGE:
        discount_value = (action.value / Decimal("100")) * total_price
    elif action.type == action.FIXED:
        discount_value = min(action.value, total_price)

    return {
        "discount_id": discount.id,
        "discount_name": discount.name,
        "value": discount_value if action.type != action.FREE_SHIPPING else None,
        "type": action.type,
        "reason": reasons,
    }
