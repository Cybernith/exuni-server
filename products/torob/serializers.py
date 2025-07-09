from rest_framework import serializers

from products.models import Product


class TorobProductSerializer(serializers.ModelSerializer):
    page_unique = serializers.IntegerField(source='id', read_only=True)
    product_group_id = serializers.IntegerField(source='variation_of.id', read_only=True)
    page_url = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()
    short_desc = serializers.SerializerMethodField()
    current_price = serializers.SerializerMethodField()
    old_price = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    image_links = serializers.SerializerMethodField()
    date_added = serializers.SerializerMethodField()
    date_updated = serializers.SerializerMethodField()
    spec = serializers.SerializerMethodField()
    guarantee = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "page_unique", "page_url", "product_group_id", "total", "title", "subtitle",
            "current_price", "old_price", "availability", "category_name",
            "image_links", "spec", "guarantee", "short_desc",
            "date_added", "date_updated"
        ]

    def get_page_url(self, obj):
        return f'https://exuni.ir/products/{obj.id}'

    def get_title(self, obj):
        if obj.product_type == Product.VARIATION:
            return f'{obj.variation_of.name} {obj.variation_title} {obj.name}'[:499]
        else:
            return obj.name

    def get_subtitle(self, obj):
        return None

    def get_short_desc(self, obj):
        if obj.explanation:
            return obj.explanation[:499]
        return None

    def get_current_price(self, obj):
        return obj.price or 0

    def get_old_price(self, obj):
        return obj.regular_price or 0

    def get_availability(self, obj):
        if hasattr(obj, 'current_inventory'):
            return obj.current_inventory.inventory > 0
        return False

    def get_total(self, obj):
        if hasattr(obj, 'current_inventory'):
            return obj.current_inventory.inventory
        return 0

    def get_category_name(self, obj):
        if obj.category.exists():
            return obj.category.first().name[:199]
        return ''

    def get_image_links(self, obj):
        links = []
        if obj.picture:
            links.append(f'https://admin.exuni.ir{obj.picture.url}')
        for image in obj.gallery.all():
            if image.picture:
                links.append(f'https://admin.exuni.ir{image.picture.url}')
        return links

    def get_date_added(self, obj):
        return obj.created_at.isoformat()

    def get_date_updated(self, obj):
        return obj.updated_at.isoformat()

    def get_spec(self, obj):
        return {}

    def get_guarantee(self, obj):
        return None
