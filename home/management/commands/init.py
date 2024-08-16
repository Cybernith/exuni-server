import os
from django.core.management import call_command
from django.core.management.base import BaseCommand

from accounts.accounts.models import Account
from accounts.defaultAccounts.models import DefaultAccount
from helpers.test import set_user
from users.models import User


class Command(BaseCommand):
    help = 'load fixtures'

    def handle(self, *args, **options):
        os.chdir("home/fixtures")
        fixtures = os.listdir()
        fixtures.sort()
        for fixture in fixtures:
            print(fixture)
            call_command('loaddata', fixture)

        set_user(User.objects.first())
        accounts = Account.objects.filter(
            financial_year_id=1,
            level=3,
            floatAccountGroup=None,
            costCenterGroup=None,
        ).all()
        for i, default_account in enumerate(DefaultAccount.objects.filter(financial_year_id=1)):
            default_account.account = accounts[i]
            default_account.save()
