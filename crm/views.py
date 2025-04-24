from django.shortcuts import render, get_object_or_404
from  rest_framework import generics, permissions

from crm.models import ShopProductViewLog
from crm.serializer import ShopProductViewLogCreateSerializer
from products.models import Product


class ShopProductLogApiView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ShopProductViewLogCreateSerializer

    def get_queryset(self):
        product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        return ShopProductViewLog.objects.filter(product=product)

