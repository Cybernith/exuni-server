import os
from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image

from server.settings import BASE_DIR


class Command(BaseCommand):
    help = "Optimize all images in MEDIA_ROOT"

    def handle(self, *args, **kwargs):
        media_root = os.path.join(BASE_DIR, 'media/uploads/images')
        for root, dirs, files in os.walk(media_root):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    file_path = os.path.join(root, file)
                    self.optimize_image(file_path)

    def optimize_image(self, file_path):
        try:
            img = Image.open(file_path)
            if img.format.lower() in ['jpeg', 'jpg']:
                img.save(file_path, "JPEG", optimize=True, quality=70)  # کیفیت ۷۰ معمولا خیلی خوبه
            elif img.format.lower() == 'png':
                img.save(file_path, "PNG", optimize=True)
            elif img.format.lower() == 'webp':
                img.save(file_path, "WEBP", quality=70, optimize=True)
            self.stdout.write(self.style.SUCCESS(f"Optimized {file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error optimizing {file_path}: {e}"))
