from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from products.models import Category, Product
from products.utils import extract_features
import numpy as np


CATEGORY_TREE_CACHE_KEY = 'category_tree_data'

@receiver([post_save, post_delete], sender=Category)
def clear_category_tree_cache(sender, **kwargs):
    cache.delete(CATEGORY_TREE_CACHE_KEY)

@receiver(post_save, sender=Product)
def save_feature_vector(sender, instance, **kwargs):
    if instance.picture and not instance.feature_vector:
        features = extract_features(instance.picture.path)
        instance.feature_vector = features.astype(np.float32).tobytes()
        instance.save()
