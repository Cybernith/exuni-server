from django.db.models.signals import post_save
from django.dispatch import receiver
import zipfile
from django.core.files.base import ContentFile
from file_handler.models import UploadedFile, ExtractedImage
from django.db import transaction


@receiver(post_save, sender=UploadedFile)
def extract_images_from_excel(sender, instance, created, **kwargs):
    if created and instance.file.name.endswith(".xlsx"):
        transaction.on_commit(lambda: process_excel_file(instance))


def process_excel_file(instance):
    xlsx_path = instance.file.path
    with zipfile.ZipFile(xlsx_path, 'r') as z:
        for name in z.namelist():
            if name.startswith("xl/media/") and not name.endswith("/"):
                img_bytes = z.read(name)
                image_file = ContentFile(img_bytes, name=f"{instance.id}_{name.split('/')[-1]}")

                ExtractedImage.objects.create(
                    uploaded_file=instance,
                    image=image_file,
                    position=name
                )
