import datetime
from django.core.management.base import BaseCommand

from companies.models import Company
from subscription.models import Extension, CompanyExtension

class Command(BaseCommand):
    help = 'active extensions'

    def add_arguments(self, parser):
        parser.add_argument('company_id', type=int)

    def handle(self, *args, **options):
        company = Company.objects.get(id=options['company_id'])
        CompanyExtension.objects.filter(company=company).delete()

        for extension in Extension.objects.all():

            CompanyExtension.objects.update_or_create(
                extension=extension,
                company=company,
                defaults={
                    'start_at': datetime.date.today(),
                    'expire_at': datetime.date.today() + datetime.timedelta(days=364)
                }
            )
