from django.db.models import Sum, F, DecimalField
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status

from affiliate.models import AffiliateFactorItem, AffiliateFactor
from affiliate.serializers import AffiliateFactorCreateSerializer
from packing.models import OrderPackage, OrderPackageItem
from products.models import Product, ProductInventory

from main.models import Business
from products.serializers import AffiliateProductRetrieveSerializer, AffiliateReceiveProductsInventorySerializer
from server.settings import DEVELOPING
from subscription.models import Factor, FactorItem, DiscountCode, Transaction
from subscription.views import TransactionCallbackView

from users.models import User
from users.serializers import UserSimpleSerializer


def get_business_from_request(req):
    business_token = req.GET.get('businessToken', None)
    if not business_token:
        raise ValidationError('توکن کسب و کار ارسال نشده')
    else:
        if Business.objects.filter(api_token=business_token).exists():
            return Business.objects.get(api_token=business_token)
        else:
            raise ValidationError('توکن کسب و کار نامعتبر میباشد')


class AffiliateFactorCreateApiView(APIView):
    permission_basename = 'affiliate_factor'

    def post(self, request):
        data = request.data
        items = data.get('products', [])
        business = get_business_from_request(self.request)
        data['business'] = business.id

        for item in items:
            if not 'product_code' and 'quantity' and 'price' in item.keys():
                raise ValidationError('ساختار ردیف ها کامل نیست')

        serializer = AffiliateFactorCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            if User.objects.filter(mobile_number=serializer.instance.phone).exists():
                customer = User.objects.get(mobile_number=serializer.instance.phone)
                if not customer.postal_code:
                    customer.postal_code = serializer.instance.postal_code
                if not customer.address:
                    customer.address = serializer.instance.address
                customer.save()
            else:
                customer = User.objects.create(
                    username=serializer.instance.phone,
                    mobile_number=serializer.instance.phone,
                    password=serializer.instance.phone,
                    first_name=serializer.instance.customer_name,
                    address=serializer.instance.address,
                    postal_code=serializer.instance.postal_code,
                    user_type=User.CUSTOMER
                )
            serializer.instance.customer = customer
            serializer.instance.save()
            business.customers.add(customer)
            business.save()
            for item in items:
                AffiliateFactorItem.objects.create(
                    affiliate_factor=serializer.instance,
                    product=Product.objects.get(id=item['product_code']),
                    quantity=item['quantity'],
                    price=item['price']
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AffiliateProductsRetrieveView(APIView):
    permission_basename = 'product'

    def get_objects(self):
        business = get_business_from_request(self.request)
        return Product.objects.filter(business=business.id)

    def get(self, request):
        query = self.get_objects()
        serializers = AffiliateProductRetrieveSerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class AffiliateReceiveProductsInventoryView(APIView):
    permission_basename = 'product'

    def get_objects(self):
        business = get_business_from_request(self.request)
        return business.products.all()

    def get(self, request):
        query = self.get_objects()
        serializers = AffiliateReceiveProductsInventorySerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class AffiliateFactorPaymentApiView(APIView):
    permission_classes = (IsAuthenticated,)
    permission_basename = 'payment_invoice'

    def post(self, request):
        data = request.data
        items = data.get('items', [])
        user = request.user
        discount_code = data.pop('discount_code', None)
        pay_from_wallet = data.pop('pay_from_wallet', False)

        business_token = data.get('business_token', [])
        if not business_token:
            raise ValidationError('توکن کسب و کار ارسال نشده')
        else:
            if Business.objects.filter(api_token=business_token).exists():
                data['business'] = Business.objects.get(api_token=business_token).id
            else:
                raise ValidationError('توکن کسب و کار نامعتبر میباشد')

        for item in items:
            if 'amount' and 'id' not in item.keys():
                raise ValidationError('ساختار ردیف ها کامل نیست')

        factor: Factor = Factor.objects.create(
            user=user,
            business=Business.objects.get(api_token=business_token),
            is_paid=False,
        )
        for item in items:
            affiliate_factor = AffiliateFactor.objects.get(pk=item['id'])
            FactorItem.objects.create(
                factor=factor,
                affiliate_factor=affiliate_factor,
                type=FactorItem.CUSTOMER_AFFILIATE_FACTOR
            )
            affiliate_factor.status = AffiliateFactor.PAID
            affiliate_factor.save()

            order_package = OrderPackage.objects.create(
                business=affiliate_factor.business,
                customer=affiliate_factor.customer,
                customer_name=affiliate_factor.customer_name,
                phone=affiliate_factor.phone,
                address=affiliate_factor.address,
                postal_code=affiliate_factor.postal_code,
            )
            for order_item in affiliate_factor.items.all():
                order_item = OrderPackageItem.objects.create(
                    order_package=order_package,
                    product=order_item.product,
                    quantity=order_item.quantity,
                    amount=order_item.price
                )
                ProductInventory.objects.get(product=order_item.product).subtract_from_inventory(order_item.quantity)

        factor.update_amounts()

        if discount_code:
            discount_code = get_object_or_404(DiscountCode, code=discount_code)
            discount_code.verify()

        payable_amount = factor.get_payable_amount()
        if pay_from_wallet:
            wallet = user.get_wallet()
            payable_amount = max(payable_amount - wallet.balance, 0)

        if payable_amount > 0:
            transaction = Transaction.create_transaction(Transaction.DEPOSIT, user, payable_amount, factor)
            return Response({
                'redirect_url': Transaction.get_redirect_url(transaction)
            })
        else:
            factor.pay()
            if DEVELOPING:
                return Response({
                    'redirect_url': 'http://localhost:8080/panel/wallet'
                })
            else:
                return Response({
                    'redirect_url': TransactionCallbackView.get_redirect_URL(True)
                })


class AffiliateCustomersView(APIView):
    permission_basename = 'user'

    def get_objects(self):
        business = get_business_from_request(self.request)
        return business.customers.all()

    def get(self, request):
        query = self.get_objects()
        serializers = UserSimpleSerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class BusinessAffiliateReportView(APIView):
    permission_basename = 'business'

    def get(self, request):
        response = []
        for business in Business.objects.all():
            affiliate_factors = AffiliateFactor.objects.filter(business=business).select_related('business')
            affiliate_factor_quantity_sum = AffiliateFactorItem.objects.filter(
                affiliate_factor__in=affiliate_factors).aggregate(Sum('quantity'))['quantity__sum']
            affiliate_factor_price_sum = AffiliateFactorItem.objects.filter(
                affiliate_factor__in=affiliate_factors).annotate(
                final_price=Sum(F('quantity') * F('price'), output_field=DecimalField()),
            ).aggregate(Sum('final_price'))['final_price__sum']

            result = {
                'business': business.name,
                'domain_address': business.domain_address,
                'factors_count': affiliate_factors.count(),
                'sale_price_sum': affiliate_factor_price_sum,
                'sale_quantity_sum': affiliate_factor_quantity_sum,
            }

            response.append(result)

        return Response(response, status=status.HTTP_200_OK)

