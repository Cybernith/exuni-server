from django.core.management.base import BaseCommand

from accounts.accounts.models import Account


class Command(BaseCommand):
    help = 'load fixtures'

    def handle(self, *args, **options):
        for account in Account.objects.all():
            account.first_name = ''
            account.last_name = ''
            account.save()
