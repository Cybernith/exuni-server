from django.db import transaction
from rest_framework import serializers

from helpers.functions import get_current_user
from main.models import Currency, Store
from products.models import Product, ProductGallery, Category, Brand
from server.store_configs import PACKING_STORE_ID
from store_handle.models import ProductStoreInventory
import json


class AdminProductGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGallery
        fields = ['id', 'picture']


class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class VariationImageField(serializers.ImageField):
    def to_internal_value(self, data):
        return super().to_internal_value(data)


class AdminVariationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    calculate_current_inventory = serializers.ReadOnlyField()
    offer_percentage = serializers.ReadOnlyField()

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Product
        exclude = ('feature_vector',)  # Add the field name you want to exclude

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_offer_percentage(self, obj):
        if obj.regular_price and obj.price:
            offer_percentage = round(((obj.regular_price - obj.price) / obj.regular_price) * 100)
            return f'{offer_percentage}%'
        return None


class AdminProductSerializer(serializers.ModelSerializer):
    calculate_current_inventory = serializers.ReadOnlyField()
    gallery = AdminProductGallerySerializer(many=True, read_only=True)
    category = AdminCategorySerializer(many=True, read_only=True)
    variations = AdminVariationSerializer(many=True, read_only=True)
    inventories_in_stores = serializers.SerializerMethodField()
    packing_inventory = serializers.SerializerMethodField()

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Product
        fields = '__all__'

    def get_inventories_in_stores(self, obj):
        store_inventories = ProductStoreInventory.objects.filter(product=obj).exclude(
            store_id=PACKING_STORE_ID).select_related('store').only('store', 'inventory')
        inventories_in_stores = []
        for store_inventory in store_inventories:
            inventories_in_stores.append(
                {
                    'store': store_inventory.store.id,
                    'name': store_inventory.store.name,
                    'inventory': store_inventory.inventory
                }
            )
        return inventories_in_stores

    def get_packing_inventory(self, obj):
        if obj.store_inventory.filter(store_id=PACKING_STORE_ID).exists():
            store_inventory = obj.store_inventory.filter(store_id=PACKING_STORE_ID).first()
            return {
                        'store': PACKING_STORE_ID,
                        'name': store_inventory.store.name,
                        'inventory': store_inventory.inventory,
                        'minimum_inventory': store_inventory.minimum_inventory
                    }
        else:
            return {
                        'store': 3213,
                        'name': '1232',
                        'inventory': 0,
                        'minimum_inventory': 0
                    }



class AdminCreateProductSerializer(serializers.ModelSerializer):
    calculate_current_inventory = serializers.ReadOnlyField()
    gallery = AdminProductGallerySerializer(many=True, read_only=True)
    image = serializers.ImageField(write_only=True, required=False)
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    currency = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
        required=False
    )
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    brand = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        required=False,
        allow_null=True
    )
    legend_pricing = serializers.BooleanField(
        required=True,
        allow_null=False,
        write_only=True,
    )
    remove_image = serializers.BooleanField(write_only=True, required=False, default=False)
    deleted_gallery_images = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        default=[]
    )

    variations = serializers.ListField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="List of variation objects"
    )
    inventories_in_stores = serializers.CharField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="List of inventory in stores"
    )

    packing_inventory = serializers.CharField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="packing store inventory"
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sixteen_digit_code', 'explanation',  'summary_explanation',  'how_to_use', 'regular_price',
            'variations',
            'price', 'currency', 'postal_weight', 'length', 'width', 'height', 'calculate_current_inventory',
            'status', 'category_ids', 'brand', 'product_type', 'image', 'images', 'gallery', 'remove_image',
            'deleted_gallery_images',
            'product_date', 'expired_date', 'legend_pricing', 'profit_type',  'profit_margin', 'discount_type',
            'discount_margin', 'base_price', 'aisle', 'shelf_number', 'inventories_in_stores', 'packing_inventory'
        ]
        extra_kwargs = {
            'sixteen_digit_code': {'required': True},
            'explanation': {'required': False, 'allow_blank': True},
            'weight': {'required': False},
            'picture': {'read_only': True},
        }

    def create(self, validated_data):
        packing_first_inventory = {
                        'store': PACKING_STORE_ID,
                        'name': 'پردازش',
                        'inventory': 0,
                        'minimum_inventory': 0
                    }
        legend_pricing = validated_data.pop('legend_pricing', False)
        packing_inventory = validated_data.pop('packing_inventory', packing_first_inventory)
        packing_inventory = json.loads(packing_inventory)

        inventories_in_stores = validated_data.pop('inventories_in_stores', [])
        inventories_in_stores = json.loads(inventories_in_stores)

        variations_data = validated_data.pop('variations', [])
        validated_data.pop('remove_image')
        validated_data.pop('deleted_gallery_images')
        image_data = validated_data.pop('image', None)
        images_data = validated_data.pop('images', [])
        category_ids = validated_data.pop('category_ids', [])
        product = Product.objects.create(**validated_data)
        ProductStoreInventory.objects.create(
            product=product,
            inventory=packing_inventory['inventory'],
            minimum_inventory=packing_inventory['minimum_inventory'],
            store=Store.objects.get(id=PACKING_STORE_ID)
        )

        if len(inventories_in_stores) > 0:
            for store_inventory in inventories_in_stores:
                if store_inventory['store']:
                    ProductStoreInventory.objects.create(
                        store=Store.objects.get(id=int(store_inventory['store'])),
                        product=product,
                        inventory=store_inventory['inventory']
                    )

        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            product.category.set(categories)

        if image_data:
            product.picture = image_data
            product.save()

        for image_data in images_data:
            ProductGallery.objects.create(product=product, picture=image_data)

        if legend_pricing and product.product_type != 'variable':
            product.set_legend_pricing()

        if variations_data:

            self.handle_variations(product, variations_data[0])


        return product

    def update(self, instance, validated_data):
        packing_first_inventory = {
                        'store': PACKING_STORE_ID,
                        'name': 'پردازش',
                        'inventory': 0,
                        'minimum_inventory': 0
                    }
        legend_pricing = validated_data.pop('legend_pricing', False)
        variations_data = validated_data.pop('variations', None)

        with transaction.atomic():
            packing_inventory = validated_data.pop('packing_inventory', packing_first_inventory)
            packing_inventory = json.loads(packing_inventory)
            packing_store_inventory, created = ProductStoreInventory.objects.get_or_create(
                product=instance, store=Store.objects.get(id=PACKING_STORE_ID)
            )
            packing_store_inventory.minimum_inventory = packing_inventory['minimum_inventory']
            packing_store_inventory.save()

            if not created and packing_store_inventory.inventory != packing_inventory['inventory']:
                packing_store_inventory.handle_inventory_in_store(packing_inventory['inventory'], get_current_user())

            inventories_in_stores = validated_data.pop('inventories_in_stores', [])
            inventories_in_stores = json.loads(inventories_in_stores)
            if len(inventories_in_stores) > 0:
                for store_inventory in inventories_in_stores:
                    if store_inventory['store']:
                        inv = ProductStoreInventory.objects.filter(
                            product=instance,
                            store=Store.objects.get(id=int(store_inventory['store']))
                        )
                        if inv.exists():
                            if inv.first().inventory != store_inventory['inventory']:
                                inv.first().handle_inventory_in_store(store_inventory['inventory'] or 0)
                        else:
                            ProductStoreInventory.objects.create(
                                store=Store.objects.get(id=int(store_inventory['store'])),
                                product=instance,
                                inventory=store_inventory['inventory'] or 0
                            )

        remove_image = validated_data.pop('remove_image', False)
        deleted_gallery_ids = validated_data.pop('deleted_gallery_images', [])
        category_ids = validated_data.pop('category_ids', [])
        image_data = validated_data.pop('image', None)
        images_data = validated_data.pop('images', [])


        for attr, value in validated_data.items():
            setattr(instance, attr, value)


        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            instance.category.set(categories)


        if remove_image:
            instance.picture = None
        elif image_data:
            instance.picture = image_data

        if deleted_gallery_ids:
            # Delete removed gallery images
            ProductGallery.objects.filter(
                id__in=deleted_gallery_ids,
                product=instance
            ).delete()

        # Add new gallery images
        for image_data in images_data:
            ProductGallery.objects.create(product=instance, picture=image_data)

        instance.save()
        instance.variations.all().update(currency=instance.currency, brand=instance.brand)

        if legend_pricing and instance.product_type != 'variable':
            instance.set_legend_pricing()

        if variations_data is not None:
            self.handle_variations(instance, variations_data[0])

        return instance

    def handle_variations(self, product, variations_data):

        existing_ids = set(product.variations.values_list('id', flat=True))
        received_ids = set()

        for variation_data in variations_data:
            legend = variation_data.pop('legend_pricing', False)

            variation_id = variation_data.get('id')

            if variation_id and variation_id in existing_ids:
                file_key = variation_data.pop('file_key', None)
                variation = Product.objects.get(id=variation_id)

                if file_key:
                    if file_key == 'remove':
                        variation.picture = None
                        variation.save()
                    elif file_key != 'same':
                        request = self.context.get('request')
                        pic = request.FILES.get(file_key)
                        variation.picture = pic
                        # ProductGallery.objects.create(product=variation.variation_of, picture=pic)

                variation.save()
                variation.update(currency=product.currency, brand=product.brand)
                new_inventory = variation_data.pop('new_inventory', 0)
                current_inventory = variation.current_inventory
                if new_inventory != current_inventory.inventory:
                    if new_inventory > current_inventory.inventory:
                        current_inventory.increase_inventory(
                            (new_inventory - current_inventory.inventory), user=get_current_user()
                        )
                    else:
                        current_inventory.reduce_inventory(
                            (current_inventory.inventory - new_inventory), user=get_current_user()
                        )

                serializer = AdminVariationSerializer(
                    variation,
                    data=variation_data,
                    partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    received_ids.add(serializer.instance.id)
                    if legend == 'true':
                        serializer.instance.set_legend_pricing()


                else:
                    raise serializers.ValidationError({
                        'variations': serializer.errors
                    })

            else:
                variation_data.pop('id')
                file_key = variation_data.pop('file_key', None)
                variation_data['variation_of'] = product.id
                variation_data['product_type'] = 'variation'
                new_inventory = variation_data.pop('new_inventory', 0)
                variation_data['first_inventory'] = new_inventory
                serializer = AdminVariationSerializer(data=variation_data)
                if serializer.is_valid():
                    serializer.save()
                    serializer.instance.update(currency=product.currency, brand=product.brand)

                    received_ids.add(serializer.instance.id)
                    if file_key != 'remove':
                        request = self.context.get('request')
                        pic = request.FILES.get(file_key)
                        serializer.instance.picture = pic
                        #ProductGallery.objects.create(product=serializer.instance.variation_of,
                        #                              picture=pic)
                    serializer.instance.currency = serializer.instance.variation_of.currency
                    serializer.instance.brand = serializer.instance.variation_of.brand
                    serializer.instance.save()
                    if legend == 'true':
                        serializer.instance.set_legend_pricing()


                else:
                    raise serializers.ValidationError({
                        'variations': serializer.errors
                    })

        # Delete variations that weren't included
        to_delete = existing_ids - received_ids
        if to_delete:
            Product.objects.filter(id__in=to_delete).delete()
