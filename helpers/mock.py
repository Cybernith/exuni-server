import jdatetime
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.accounts.models import Account
from accounts.accounts.permissions import AccountListCreate
from companies.models import FinancialYear
from sanads.models import Sanad, newSanadCode
from users.models import User


def create_accounts(self):
    financial_year = FinancialYear.objects.get(pk=2)
    accounts = Account.objects.inFinancialYear(financial_year).filter(level=2).all()
    accounts_count = len(accounts)
    for i in range(500):
        print(i)
        factory = APIRequestFactory()
        request = factory.post('/accounts/accounts', {
            'account_type': 'o',
            'parent': accounts[i % accounts_count].id,
            'name': 'حساب تست #{}'.format(i)
        })
        force_authenticate(request, user=User.objects.get(pk=1))
        view = AccountListCreate.as_view()
        view(request)


def create_sanads(self):
    financial_year = FinancialYear.objects.get(pk=2)
    accounts = Account.objects.inFinancialYear(financial_year).filter(level=3).all()[:100]
    accounts_count = len(accounts)

    for i in range(10000):
        sanad = Sanad.objects.create(
            financial_year=financial_year,
            code=newSanadCode(),
            date=jdatetime.date.today()
        )
        for j in range(10):
            if i % 2 == 0:
                bed = 1000
                bes = 0
            else:
                bed = 0
                bes = 1000
            sanad.items.create(
                financial_year=financial_year,
                account=accounts[i * j % accounts_count],
                bed=bed,
                bes=bes
            )
