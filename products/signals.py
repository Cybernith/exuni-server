from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from products.models import Category, Product
import numpy as np
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from products.utils import ImageFeatureExtractor

CATEGORY_TREE_CACHE_KEY = 'category_tree_data'

@receiver([post_save, post_delete], sender=Category)
def clear_category_tree_cache(sender, **kwargs):
    cache.delete(CATEGORY_TREE_CACHE_KEY)


extractor = ImageFeatureExtractor()

@receiver(post_save, sender=Product)
def save_feature_vector(sender, instance, **kwargs):
    if instance.picture and not instance.feature_vector:
        try:
            features = extractor.extract_features(instance.picture)
            instance.feature_vector = features.astype(np.float32).tobytes()
            instance.save(update_fields=['feature_vector'])
        except Exception as exception:
            pass

