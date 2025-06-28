from django.db import models
from django.db.models import OuterRef, Subquery, Value, IntegerField, Sum, F
from django.db.models.functions import Coalesce
from django.db.models import Case, When


class ProductQuerySet(models.QuerySet):
    def with_inventory_count(self):
        from products.models import ProductInventory, Product
        variations_inventory_subquery = ProductInventory.objects.filter(
            product__variation_of=OuterRef('pk')
        ).values('product__variation_of').annotate(
            total_inventory=Sum('inventory')
        ).values('total_inventory')

        return self.annotate(
            own_inventory=Coalesce(
                Subquery(
                    ProductInventory.objects.filter(product=OuterRef('pk')).values('inventory')[:1],
                ),
                Value(0),
                output_field=IntegerField()
            ),
            variations_inventory=Coalesce(
                Subquery(
                    variations_inventory_subquery,
                    output_field=IntegerField()
                ),
                Value(0),
                output_field=IntegerField()
            )
        ).annotate(
            inventory_count=Case(
                When(product_type=Product.VARIABLE, then='variations_inventory'),
                default='own_inventory',
                output_field=IntegerField()
            )
        )

    def order_out_of_stock_inventory_last(self):
        return self.with_inventory_count().order_by(
            Case(
                When(inventory_count=0, then=1),
                default=0,
                output_field=IntegerField()
            ),
            'inventory_count',
            'pk'
        )

    def published(self):
        from products.models import Product
        return self.filter(
            status=Product.PUBLISHED,
        )

    def main_products(self):
        from products.models import Product

        return self.filter(
            product_type__in=[Product.VARIABLE, Product.SIMPLE]
        )

    def shop_products(self):
        from products.models import ProductInventory, Product

        variations_inventory_sq = (
            ProductInventory.objects
            .filter(product__variation_of=OuterRef('pk'))
            .values('product__variation_of')
            .annotate(total=Sum('inventory'))
            .values('total')
        )

        own_inventory_sq = (
            ProductInventory.objects
            .filter(product=OuterRef('pk'))
            .order_by('id')
            .values('inventory')[:1]
        )

        return (
            self.filter(
                status=Product.PUBLISHED,
                product_type__in=[Product.SIMPLE, Product.VARIABLE]
            )
            .annotate(
                own_inventory=Coalesce(
                    Subquery(own_inventory_sq),
                    Value(0),
                    output_field=IntegerField()
                ),
                variations_inventory=Coalesce(
                    Subquery(variations_inventory_sq, output_field=IntegerField()),
                    Value(0),
                    output_field=IntegerField()
                ),
                inventory_count=Case(
                    When(product_type=Product.VARIABLE, then=F('variations_inventory')),
                    default=F('own_inventory'),
                    output_field=IntegerField()
                )
            )
            .order_by(
                Case(When(inventory_count=0, then=1), default=0, output_field=IntegerField()),
                '-inventory_count',
                'pk'
            )
        )


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db).shop_products()

    def out_of_stock_inventory_at_last(self):
        return self.get_queryset().order_out_of_stock_inventory_last()

    def published(self):
        return self.get_queryset().published()

    def main_products(self):
        return self.get_queryset().main_products()

    def shop_products(self):
        return self.get_queryset().shop_products()
