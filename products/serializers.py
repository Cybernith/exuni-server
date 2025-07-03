from rest_framework import serializers
import os
from entrance.models import StoreReceiptItem
from helpers.functions import change_to_num
from helpers.serializers import SModelSerializer
from products.models import Brand, Avail, ProductProperty, Category, Product, ProductGallery, ProductInventory, \
    ProductPrice, ProductPriceHistory, Feature, Categorization
from server.settings import BASE_DIR, SERVER_URL
from users.serializers import UserSimpleSerializer

from django.db.models import Sum, IntegerField, Q, Count, F


class BrandSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    logo = serializers.ImageField(required=False, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Brand
        fields = '__all__'


class BrandShopListSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'logo_url')

    def get_logo_url(self, obj):
        return obj.logo.url if obj.logo else None


class BrandLogoUpdateSerializer(SModelSerializer):
    logo = serializers.ImageField(required=False)

    class Meta:
        read_only_fields = ('created_at', 'updated_at', 'name', 'is_domestic', 'made_in', 'supplier')
        model = Brand
        fields = ('id', 'logo', 'created_at', 'updated_at', 'name', 'is_domestic', 'made_in', 'supplier')


class ProductPictureUpdateSerializer(SModelSerializer):
    picture = serializers.ImageField(required=False)

    class Meta:
        model = Product
        fields = ('id', 'picture')


class AvailSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Avail
        fields = '__all__'


class AvailTreeRootSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Avail
        fields = ('id', 'name', 'explanation', 'image')

    def get_image(self, obj):
        return 'https://admin.exuni.ir' + obj.image.url if obj.image else None


class FeatureTreeRootSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Feature
        fields = ('id', 'name', 'explanation', 'image')

    def get_image(self, obj):
        return 'https://admin.exuni.ir' + obj.image.url if obj.image else None


class CategorizationRootSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Categorization
        fields = ('id', 'name', 'explanation', 'image')

    def get_image(self, obj):
        return 'https://admin.exuni.ir' + obj.image.url if obj.image else None


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

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ProductGallery
        fields = '__all__'


class ProductForLogSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Product
        fields = 'name', 'id'


class ProductSimpleSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Product
        fields = 'created_by', 'updated_at', 'name', 'id', 'barcode', 'sixteen_digit_code', 'summary_explanation'


class ProductOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = 'name', 'id', 'barcode', 'sixteen_digit_code', 'shelf_code', 'picture'


class ProductContentDevelopmentSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at', 'picture')
        model = Product
        fields = 'created_by', 'updated_at', 'name', 'picture', 'id', 'barcode',\
                 'explanation', 'how_to_use', 'summary_explanation', 'category'


class NoContentProductSimpleSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    has_explanation = serializers.SerializerMethodField(read_only=True)
    has_picture = serializers.SerializerMethodField(read_only=True)
    has_summary_explanation = serializers.SerializerMethodField(read_only=True)
    has_how_to_use = serializers.SerializerMethodField(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at', 'picture')
        model = Product
        fields = 'created_by', 'updated_at', 'name', 'id', 'barcode', 'has_explanation', 'has_picture',\
                 'has_summary_explanation', 'has_how_to_use', 'picture'

    def get_has_explanation(self, obj: Product):
        if obj.explanation:
            return True
        else:
            return False

    def get_has_picture(self, obj: Product):
        if obj.picture:
            return True
        else:
            return False

    def get_has_summary_explanation(self, obj: Product):
        if obj.summary_explanation:
            return True
        else:
            return False

    def get_has_how_to_use(self, obj: Product):
        if obj.how_to_use:
            return True
        else:
            return False


class ProductSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    avails = AvailSerializer(many=True, read_only=True)
    properties = ProductPropertySerializer(many=True, read_only=True)
    category = CategorySerializer(many=True, read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    made_in = serializers.ReadOnlyField()
    rate = serializers.ReadOnlyField()
    is_domestic = serializers.ReadOnlyField()
    is_freeze = serializers.ReadOnlyField()
    is_expired_closed = serializers.ReadOnlyField()
    content_production_completed = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    inventory = serializers.SerializerMethodField()

    def get_inventory(self, obj: Product):
        return obj.current_inventory.inventory

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Product
        fields = '__all__'


class AffiliateProductRetrieveSerializer(serializers.ModelSerializer):
    product_code = serializers.CharField(source='barcode', read_only=True)
    title = serializers.CharField(source='name', read_only=True)
    description = serializers.CharField(source='explanation', read_only=True)
    features = serializers.CharField(source='summary_explanation', read_only=True)
    weight = serializers.IntegerField(source='postal_weight', read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    stock = serializers.SerializerMethodField(read_only=True)
    min_stock = serializers.IntegerField(source='min_inventory', read_only=True)
    type = serializers.ReadOnlyField()
    images = serializers.SerializerMethodField(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Product
        fields = 'created_by', 'updated_at', 'id', 'product_code', 'title', 'description', 'features', 'weight',\
                 'price', 'stock', 'min_stock', 'type', 'group_id', 'images'

    def get_stock(self, obj: Product):
        return ProductInventory.objects.get(product=obj).inventory

    def get_images(self, obj: Product):

        images = []
        images.append(SERVER_URL + obj.picture.url)
        for gallery in ProductGallery.objects.filter(product=obj):
            images.append(SERVER_URL + gallery.picture.url)
        return images

    def get_price(self, obj: Product):
        return ProductInventory.objects.get(product=obj).price


class AffiliateReceiveProductsInventorySerializer(serializers.ModelSerializer):
    product_code = serializers.CharField(source='barcode', read_only=True)
    stock = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = 'product_code', 'stock'

    def get_stock(self, obj: Product):
        return ProductInventory.objects.get(product=obj).inventory


class ProductPriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPriceHistory
        fields = ['previous_price', 'new_price', 'changed_at', 'changed_by', 'note']


class AvailTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Avail
        fields = ['id', 'name', 'explanation', 'parent', 'children']

    def get_children(self, obj):
        children = obj.children.all()
        serializer = AvailTreeSerializer(children, many=True)
        return serializer.data


