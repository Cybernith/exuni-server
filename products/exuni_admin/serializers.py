from rest_framework import serializers

from helpers.functions import get_current_user
from main.models import Currency
from products.models import Product, ProductGallery, Category, Brand


class AdminProductGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGallery
        fields = ['id', 'picture']


class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']  # Or whatever fields you want to expose

class VariationImageField(serializers.ImageField):
    def to_internal_value(self, data):
        return super().to_internal_value(data)


class AdminVariationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    calculate_current_inventory = serializers.ReadOnlyField()

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Product
        exclude = ('feature_vector',)  # Add the field name you want to exclude

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

class AdminProductSerializer(serializers.ModelSerializer):
    calculate_current_inventory = serializers.ReadOnlyField()
    gallery = AdminProductGallerySerializer(many=True, read_only=True)
    category = AdminCategorySerializer(many=True, read_only=True)
    variations = AdminVariationSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Product
        fields = '__all__'


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
    new_inventory = serializers.IntegerField(
        required=True,
        allow_null=True
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

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sixteen_digit_code', 'explanation',  'summary_explanation',  'how_to_use', 'regular_price', 'variations',
            'price', 'currency', 'new_inventory', 'postal_weight', 'length', 'width', 'height', 'calculate_current_inventory',
            'status', 'category_ids', 'brand', 'product_type', 'image', 'images', 'gallery', 'remove_image', 'deleted_gallery_images'
        ]
        extra_kwargs = {
            'sixteen_digit_code': {'required': True},
            'explanation': {'required': False, 'allow_blank': True},
            'first_inventory': {'required': False},
            'weight': {'required': False},
            'picture': {'read_only': True},
        }


    def validate(self, data):
        if 'price' in data and 'regular_price' in data:
            if data['price'] > data['regular_price']:
                raise serializers.ValidationError(
                    {'price': 'Sale price cannot be higher than regular price'}
                )

        return data

    def create(self, validated_data):
        variations_data = validated_data.pop('variations', [])
        validated_data.pop('remove_image')
        validated_data.pop('deleted_gallery_images')
        image_data = validated_data.pop('image', None)
        new_inventory = validated_data.pop('new_inventory', 0)
        validated_data['first_inventory'] = new_inventory
        images_data = validated_data.pop('images', [])
        category_ids = validated_data.pop('category_ids', [])
        # Create the product
        product = Product.objects.create(**validated_data)

        if variations_data:
            self.handle_variations(product, variations_data[0])


        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            product.category.set(categories)

        if image_data:
            product.picture = image_data
            product.save()

        for image_data in images_data:
            ProductGallery.objects.create(product=product, picture=image_data)

        return product

    def update(self, instance, validated_data):
        variations_data = validated_data.pop('variations', None)
        new_inventory = validated_data.pop('new_inventory', 0)
        remove_image = validated_data.pop('remove_image', False)
        deleted_gallery_ids = validated_data.pop('deleted_gallery_images', [])
        category_ids = validated_data.pop('category_ids', [])
        image_data = validated_data.pop('image', None)
        images_data = validated_data.pop('images', [])

        current_inventory = instance.current_inventory
        if new_inventory != current_inventory.inventory:
            if new_inventory > current_inventory.inventory:
                current_inventory.increase_inventory(
                    (new_inventory - current_inventory.inventory), user=get_current_user()
                )
            else:
                current_inventory.reduce_inventory(
                    (current_inventory.inventory - new_inventory), user=get_current_user()
                )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if variations_data is not None:
            self.handle_variations(instance, variations_data[0])

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
        return instance

    def handle_variations(self, product, variations_data):

        existing_ids = set(product.variations.values_list('id', flat=True))
        received_ids = set()

        for variation_data in variations_data:

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
                        variation.picture = request.FILES[file_key]
                        variation.save()

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
                    received_ids.add(serializer.instance.id)
                    if file_key != 'remove':
                        request = self.context.get('request')
                        serializer.instance.picture = request.FILES[file_key]
                        serializer.instance.save()

                else:
                    raise serializers.ValidationError({
                        'variations': serializer.errors
                    })

        # Delete variations that weren't included
        to_delete = existing_ids - received_ids
        if to_delete:
            Product.objects.filter(id__in=to_delete).delete()
