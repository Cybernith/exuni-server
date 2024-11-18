from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from entrance.models import StoreReceiptItem
from entrance.serializers import StoreReceiptItemSerializer
from helpers.auth import BasicObjectPermission
from rest_framework.views import APIView
from django.http import Http404

from rest_framework.response import Response
from rest_framework import status

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics
from helpers.models import manage_files
from django.db.models import QuerySet, Q

from affiliate.models import AffiliateFactorItem, AffiliateFactor
from affiliate.serializers import AffiliateFactorCreateSerializer
from helpers.auth import BasicObjectPermission
from products.models import Product

from main.models import Business

from users.models import User


class AffiliateFactorCreateApiView(APIView):
    permission_basename = 'affiliate_factor'

    def post(self, request):
        data = request.data
        items = data.get('products', [])
        business_token = self.request.GET.get('businessToken', None)
        if not business_token:
            raise ValidationError('توکن فروشگاه ارسال نشده')
        else:
            if Business.objects.filter(api_token=business_token).exists():
                business = Business.objects.get(api_token=business_token)
            else:
                raise ValidationError('توکن فروشگاه نامعتبر میباشد')

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
