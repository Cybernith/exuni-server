from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from django.contrib.auth.management import create_permissions
from django.template.backends import django


class Command(BaseCommand):
    help = 'deletes all permissions and recreate them'

    def handle(self, *args, **options):
        Permission.objects.all().delete()
        apps = []
        for model in django.apps.get_models():
            apps.append(django.apps.get_app_config(model._meta.app_label))
        for app in apps:
            create_permissions(app, 0)
