from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

class CustomUploadStorage(FileSystemStorage):

    def __init__(self, *args, **kwargs):
        location = kwargs.get('location') or os.path.join(settings.MEDIA_ROOT, 'uploads')
        base_url = kwargs.get('base_url') or os.path.join(settings.MEDIA_URL, 'uploads/')
        super().__init__(location=location, base_url=base_url)

