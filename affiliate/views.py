from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status

from affiliate.models import AffiliateFactorItem, AffiliateFactor, PaymentInvoiceItem
from affiliate.serializers import AffiliateFactorCreateSerializer, PaymentInvoiceCreateSerializer
from products.models import Product

from main.models import Business
from products.serializers import AffiliateProductRetrieveSerializer, AffiliateReceiveProductsInventorySerializer

from users.models import User


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
        return Product.objects.filter(business=business.id)

    def get(self, request):
        query = self.get_objects()
        serializers = AffiliateReceiveProductsInventorySerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class PaymentInvoiceCreateApiView(APIView):
    permission_classes = (IsAuthenticated,)
    permission_basename = 'payment_invoice'

    def post(self, request):
        data = request.data
        items = data.get('items', [])

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

        serializer = PaymentInvoiceCreateSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            for item in items:
                factor = AffiliateFactor.objects.get(pk=item['id'])
                PaymentInvoiceItem.objects.create(
                    payment_invoice=serializer.instance,
                    amount=item['amount'],
                    affiliate_factor=factor,
                    type=PaymentInvoiceItem.CUSTOMER_AFFILIATE_FACTOR
                )
                factor.status = AffiliateFactor.IN_PROCESSING
                factor.save()
            serializer.instance.set_amount()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


