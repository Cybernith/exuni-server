from rest_framework import serializers

from products.models import Brand, Avail, ProductProperty, Category, Product, ProductGallery


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Brand
        fields = '__all__'


class AvailSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Avail
        fields = '__all__'


class ProductPropertySerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ProductProperty
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Category
        fields = '__all__'


class ProductGallerySerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ProductGallery
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    gallery = ProductGallerySerializer(many=True, read_only=True)
    avails = AvailSerializer(many=True, read_only=True)
    properties = ProductPropertySerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    brand = CategorySerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Product
        fields = '__all__'


