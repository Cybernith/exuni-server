from rest_framework import serializers

from helpers.serializers import SModelSerializer
from products.models import Brand, Avail, ProductProperty, Category, Product, ProductGallery
from users.serializers import UserSimpleSerializer


class BrandSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at', 'logo')
        model = Brand
        fields = '__all__'


class BrandLogoUpdateSerializer(SModelSerializer):
    logo = serializers.ImageField(required=False)

    class Meta:
        model = Brand
        fields = ('id', 'logo')


class AvailSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Avail
        fields = '__all__'


class ProductPropertySerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ProductProperty
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at', 'picture')
        model = Category
        fields = '__all__'


class CategoryPictureUpdateSerializer(SModelSerializer):
    picture = serializers.ImageField(required=False)

    class Meta:
        model = Category
        fields = ('id', 'picture')


class ProductGallerySerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ProductGallery
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    gallery = ProductGallerySerializer(many=True, read_only=True)
    avails = AvailSerializer(many=True, read_only=True)
    properties = ProductPropertySerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    brand = CategorySerializer(read_only=True)
    made_in = serializers.ReadOnlyField()
    is_domestic = serializers.ReadOnlyField()
    inventory = serializers.ReadOnlyField()
    is_freeze = serializers.ReadOnlyField()
    is_expired_closed = serializers.ReadOnlyField()
    content_production_completed = serializers.ReadOnlyField()

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Product
        fields = '__all__'


