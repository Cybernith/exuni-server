import re

from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from products.models import Product
from products.torob.functions import verify_torob_jwt_token
from products.torob.serializers import TorobProductSerializer

PAGE_SIZE = 100


class TorobProductAPIView(APIView):
    def post(self, request):
        # token = request.headers.get("X-Torob-Token")
        # audience = request.get_host()
        # if not token or not verify_torob_jwt_token(token, audience):
        #     return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        if "page_urls" in data:
            urls = data["page_urls"]
            if not isinstance(urls, list) or not urls:
                return Response({"error": "invalid page_urls"}, status=status.HTTP_400_BAD_REQUEST)

            product_ids = []
            for url in urls:
                match = re.search(r"/product/(\d+)/?$", url)
                if match:
                    product_ids.append(match.group(1))
                else:
                    return Response({"error": f"{url} is invalid (dont have this product)"},
                                    status=status.HTTP_400_BAD_REQUEST)

            qs = Product.objects.filter(status=Product.PUBLISHED).exclude(product_type=Product.VARIABLE)

            products = qs.filter(Q(product_id__in=product_ids) | Q(id__in=product_ids))
            serialized = TorobProductSerializer(products, many=True)

            return Response({
                "api_version": "torob_api_v3",
                "current_page": 1,
                "total": len(products),
                "max_pages": 1,
                "products": serialized.data
            })

        elif "page_uniques" in data:
            ids = data["page_uniques"]
            if not isinstance(ids, list) or not ids:
                return Response({"error": "invalid page_uniques"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                ids_list = [int(x) for x in ids]
            except ValueError:
                return Response({"error": "Invalid page_uniques found"}, status=status.HTTP_400_BAD_REQUEST)

            qs = Product.objects.filter(status=Product.PUBLISHED).exclude(product_type=Product.VARIABLE)
            products = qs.filter(Q(product_id__in=ids_list) | Q(id__in=ids_list))

            serialized = TorobProductSerializer(products, many=True)

            return Response({
                "api_version": "torob_api_v3",
                "current_page": 1,
                "total": len(products),
                "max_pages": 1,
                "products": serialized.data
            })

        if "sort" not in data:
            return Response({"error": "sort parameter is not provided"}, status=status.HTTP_400_BAD_REQUEST)
        if "page" not in data:
            return Response({"error": "page parameter is not provided"}, status=status.HTTP_400_BAD_REQUEST)

        if "page" in data and "sort" in data:
            try:
                page = int(data["page"])
                sort = data["sort"]
                if sort not in ["date_added_desc", "date_updated_desc"]:
                    raise ValueError()
            except ValueError:
                return Response({"error": "invalid page or sort value"}, status=status.HTTP_400_BAD_REQUEST)

            qs = Product.objects.filter(status=Product.PUBLISHED).exclude(product_type=Product.VARIABLE)

            if sort == "date_added_desc":
                qs = qs.order_by("-created_at")
            elif sort == "date_updated_desc":
                qs = qs.order_by("-updated_at")

            total = qs.count()
            max_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
            products = qs[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]
            serialized = TorobProductSerializer(products, many=True)

            return Response({
                "api_version": "torob_api_v3",
                "current_page": page,
                "total": total,
                "max_pages": max_pages,
                "products": serialized.data
            })

        return Response({"error": "Invalid request body"}, status=status.HTTP_400_BAD_REQUEST)


