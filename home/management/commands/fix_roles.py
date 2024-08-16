from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from django.db.models import Q


class Command(BaseCommand):
    help = 'fix payroll'

    def handle(self, *args, **options):

        for permission in Permission.objects.filter(Q(codename__contains='contract') & Q(content_type__app_label='payroll')
                                                    & Q(name__contains='وام')):
            permission.delete()



