from rest_framework import serializers
import json
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
    calculate_current_inventory = serializers.ReadOnlyField()
    picture = VariationImageField(required=False, allow_null=True)
    remove_picture = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Product
        exclude = ('feature_vector',)  # Add the field name you want to exclude



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
        required=True
    )
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True
    )

    brand = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        required=False,
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
            'price', 'currency', 'first_inventory', 'postal_weight', 'length', 'width', 'height', 'calculate_current_inventory',
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
        images_data = validated_data.pop('images', [])
        category_ids = validated_data.pop('category_ids', [])
        print(variations_data, flush=True)
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
            print('ga', flush=True)
            ProductGallery.objects.create(product=product, picture=image_data)

        return product

    def update(self, instance, validated_data):
        variations_data = validated_data.pop('variations', None)

        remove_image = validated_data.pop('remove_image', False)
        deleted_gallery_ids = validated_data.pop('deleted_gallery_images', [])
        category_ids = validated_data.pop('category_ids', [])
        image_data = validated_data.pop('image', None)
        images_data = validated_data.pop('images', [])

        # Update scalar fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if variations_data is not None:
            self.handle_variations(instance, variations_data[0])

        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            instance.category.set(categories)


        # Handle main image
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
                # Update existing variation
                variation = Product.objects.get(id=variation_id)
                serializer = AdminVariationSerializer(
                    variation,
                    data=variation_data,
                    partial=True
                )
            else:
                # Create new variation
                variation_data['variation_of'] = product.id
                variation_data['product_type'] = 'variation'
                serializer = AdminVariationSerializer(data=variation_data)

            if serializer.is_valid():
                serializer.save()
                received_ids.add(serializer.instance.id)
            else:
                raise serializers.ValidationError({
                    'variations': serializer.errors
                })

        # Delete variations that weren't included
        to_delete = existing_ids - received_ids
        if to_delete:
            Product.objects.filter(id__in=to_delete).delete()
