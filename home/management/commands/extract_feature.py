from django.core.management import BaseCommand
from django.db.models import Q

from products.models import Product
from products.utils import ImageFeatureExtractor
import numpy as np

extractor = ImageFeatureExtractor()

class Command(BaseCommand):
    help = 'extract feature'

    def handle(self, *args, **options):
        for product in Product.objects.all():
            if product.picture and not product.feature_vector:
                try:
                    features = extractor.extract_features(product.picture)
                    product.feature_vector = features.astype(np.float32).tobytes()
                    product.save(update_fields=['feature_vector'])
                except Exception as exception:
                    print(exception)





