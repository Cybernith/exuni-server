from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from products.models import Category

CATEGORY_TREE_CACHE_KEY = 'category_tree_data'


@receiver([post_save, post_delete], sender=Category)
def clear_category_tree_cache(sender, **kwargs):
    cache.delete(CATEGORY_TREE_CACHE_KEY)