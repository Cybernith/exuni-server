from django.shortcuts import render, get_object_or_404
from  rest_framework import generics, permissions

from crm.models import ShopProductViewLog
from crm.serializer import ShopProductViewLogCreateSerializer
from products.models import Product

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.db.models.functions import TruncMonth

class ShopProductLogApiView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ShopProductViewLogCreateSerializer

    def get_queryset(self):
        product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        return ShopProductViewLog.objects.filter(product=product)


class ProductViewSummaryAPIView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        total_views = ShopProductViewLog.objects.filter(product=product).count()

        monthly_qs = (
            ShopProductViewLog.objects
            .filter(product=product)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(views=Count('id'))
            .order_by('month')
        )
        monthly_data = [
            {
                "month": entry['month'].strftime("%Y-%m"),
                "views": entry['views']
            }
            for entry in monthly_qs
        ]

        return Response({
            "product_id": product_id,
            "total_views": total_views,
            "monthly_views": monthly_data
        }, status=status.HTTP_200_OK)
