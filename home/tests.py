import datetime

from django.test import TestCase

# Create your tests here.
import logging

import factory
from django.urls import reverse
from rest_framework import status

from accounts.accounts.models import Account, AccountType
from accounts.coding import Coding
from companies.models import Company, FinancialYear
from helpers.functions import date_to_str
from helpers.middlewares.modify_request_middleware import ModifyRequestMiddleware
from helpers.test import MTestCase
from subscription.constants import FEATURES, MODULES
from subscription.models import Plan
from users.models import User
from wares.models import Ware, Warehouse, SalePrice, Unit

from factors.models import Factor, FactorItem
from wares.models import WareInventory
from home.test_functions import send_test_factor, get_expected_inventory_count


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')


class PlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Plan

    users_count = 1
    features = [f[0] for f in FEATURES]
    modules = [m[0] for m in MODULES]


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    superuser = factory.SubFactory(UserFactory)
    plan = factory.SubFactory(PlanFactory)
    users_count = factory.SelfAttribute('plan.users_count')
    modules = factory.SelfAttribute('plan.modules')
    features = factory.SelfAttribute('plan.features')
    expired_at = factory.LazyAttribute(lambda o: datetime.date.today() + datetime.timedelta(days=30))


class FinancialYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FinancialYear

    name = factory.Faker('first_name')
    warehouse_system = FinancialYear.DAEMI
    start = datetime.date.today()
    end = datetime.date.today() + datetime.timedelta(days=365)

    company = factory.SubFactory(CompanyFactory)

    @classmethod
    def _create(cls, *args, **kwargs):
        financial_year = super()._create(*args, **kwargs)

        Coding(financial_year).initialize()

        user = financial_year.company.superuser
        user.active_company = financial_year.company
        user.active_financial_year = financial_year
        user.save()

        return financial_year


class WarehouseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Warehouse

    name = factory.Faker('first_name')


class UnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Unit

    name = factory.Faker('name')


class SalePriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SalePrice

    unit = factory.SubFactory(UnitFactory)


class WareFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ware

    financial_year = factory.SubFactory(FinancialYearFactory)
    level = Ware.WARE
    name = factory.Faker('name')
    is_service = False

    code = factory.LazyAttribute(lambda o: o.parent.get_new_child_code() if getattr(o, 'parent', None) else Ware.get_new_nature_code(o.is_service))

    warehouse = factory.SubFactory(WarehouseFactory, financial_year=financial_year)
    salePrices = factory.RelatedFactory(SalePriceFactory, factory_related_name='ware')
    pricingType = Ware.FIFO

    @staticmethod
    def createTree(financial_year, **kwargs):
        parent = None
        for level in range(4):
            if level == Ware.WARE:
                return WareFactory.create(
                    financial_year=financial_year,
                    level=level,
                    parent=parent,
                    **kwargs
                )
            else:
                parent = WareFactory.create(
                    financial_year=financial_year,
                    level=level,
                    parent=parent,
                    warehouse=None, salePrices=None, pricingType=None
                )


class AccountTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccountType

    name = factory.Faker('first_name')
    codename = factory.Faker('first_name')
    nature = factory.Iterator(('bed', 'bes'))
    usage = factory.Iterator((AccountType.INCOME_STATEMENT, AccountType.BALANCE_SHEET, AccountType.NONE))


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    financial_year = factory.SubFactory(FinancialYearFactory)

    name = factory.Faker('first_name')
    level = Account.TAFSILI
    code = factory.LazyAttribute(lambda o: o.parent.get_new_child_code() if getattr(o, 'parent', None) else Account.get_new_group_code())

    type = factory.SubFactory(AccountTypeFactory)

    @staticmethod
    def createTree(financial_year, **kwargs):
        parent = None
        account_type = kwargs.get('type')
        for level in range(4):
            if level == Account.TAFSILI:
                return AccountFactory.create(
                    financial_year=financial_year,
                    level=level,
                    parent=parent,
                    type=account_type,
                    **kwargs
                )
            else:
                account_type = AccountTypeFactory.create()
                parent = AccountFactory.create(
                    financial_year=financial_year,
                    level=level,
                    parent=parent,
                    type=account_type
                )


class FactorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Factor

    class Params:
        factor_type = 'buy'

    financial_year = factory.SubFactory(FinancialYearFactory)
    temporary_code = factory.sequence(lambda n: n)
    code = factory.sequence(lambda n: n)
    type = factory.LazyAttribute(lambda o: o.factor_type)
    date = datetime.date.today()
    time = datetime.datetime.now().time()


class FactorItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FactorItem

    financial_year = factory.SubFactory(FinancialYearFactory)
    factor = factory.SubFactory(FactorFactory)
    ware = factory.LazyAttribute(lambda obj: WareFactory.createTree(obj.financial_year))
    unit = factory.LazyAttribute(lambda obj: obj.ware.salePrices.first().unit)
    warehouse = factory.LazyAttribute(lambda obj: obj.ware.warehouse)
    unit_count = 2
    count = 2
    fee = 1600000


class HomeTest(MTestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        pass


class FactorTest(MTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        financial_year = FinancialYearFactory.create()
        cls.financial_year = financial_year
        cls.user = financial_year.company.superuser

        ware = WareFactory.createTree(financial_year)
        cls.ware = ware
        unit = ware.salePrices.first().unit
        cls.unit = unit

        account = Account.objects.inFinancialYear(financial_year).filter(level=Account.TAFSILI).first()
        cls.account = account

        cls.data = {
            "item": {
                "taxPercent": 0,
                "taxValue": 0,
                "discountPercent": 0,
                "discountValue": 0,
                "expenses": [],
                "date": date_to_str(financial_year.start),
                "time": "14:48",
                "account": account.id,
                "type": "buy"
            },
            "items": {
                "items": [{
                    "discountValue": 0,
                    "discountPercent": 0,
                    "fee": "1600000",
                    "ware": ware.id,
                    "unit": unit.id,
                    "warehouse": ware.warehouse.id,
                    "count": "2",
                    "unit_count": "2"
                }],
                "ids_to_delete": []
            },
            "expenses": {
                "items": [],
                "ids_to_delete": []
            }
        }

    def setUp(self):
        self.client.force_authenticate(self.user)
        ModifyRequestMiddleware.user = self.user

    def test_create_factor(self):
        response = self.client.post(reverse('factor-list'), data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        inventory_count = WareInventory.objects.get(ware=self.ware, warehouse=self.ware.warehouse).count
        self.assertEqual(inventory_count, int(self.data["items"]["items"][0]["count"]))

    def test_retrieve_factor(self):
        response = self.client.post(reverse('factor-list'), data=self.data, format='json')
        factor_id = response.json()['id']

        # retrieve
        response = self.client.get(reverse('factor-detail', args=[factor_id]), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_factor(self):
        response = self.client.post(reverse('factor-list'), data=self.data, format='json')
        factor_id = response.json()['id']

        # update
        self.data["items"]["items"][0]["count"] = '10'
        response = self.client.put(reverse('factor-detail', args=[factor_id]), data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        inventory_count = WareInventory.objects.get(ware=self.ware, warehouse=self.ware.warehouse).count
        self.assertEqual(inventory_count, int(self.data["items"]["items"][0]["count"]))

    def test_delete_factor(self):
        response = self.client.post(reverse('factor-list'), data=self.data, format='json')
        factor_id = response.json()['id']

        # delete
        response = self.client.delete(reverse('factor-detail', args=[factor_id]), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # # should inventory count be equal to 0 ?
        # inventory_count = WareInventory.objects.get(ware=self.ware, warehouse=self.ware.warehouse).count
        # self.assertEqual

    def test_multiple_factors(self):

        # factor 'buy' 1
        count = int(self.data["items"]["items"][0]["count"])
        self.client.post(reverse('factor-list'), data=self.data, format='json')

        # factor 'buy' 2
        self.data["items"]["items"][0]["count"] = '10'
        count += int(self.data["items"]["items"][0]["count"])
        self.client.post(reverse('factor-list'), data=self.data, format='json')

        # check inventory count
        inventory_count = WareInventory.objects.get(ware=self.ware, warehouse=self.ware.warehouse).count
        self.assertEqual(inventory_count, count)

        # factor 'sale' 1
        self.data["item"]["type"] = 'sale'
        self.data["items"]["items"][0]["count"] = '7'
        if count > int(self.data["items"]["items"][0]["count"]):
            count -= int(self.data["items"]["items"][0]["count"])
        self.client.post(reverse('factor-list'), data=self.data, format='json')

        # check inventory count
        inventory_count = WareInventory.objects.get(ware=self.ware, warehouse=self.ware.warehouse).count
        self.assertEqual(inventory_count, count)

        # factor 'sale' 2
        self.data["item"]["type"] = 'sale'
        self.data["items"]["items"][0]["count"] = '2'
        if count > int(self.data["items"]["items"][0]["count"]):
            count -= int(self.data["items"]["items"][0]["count"])
        self.client.post(reverse('factor-list'), data=self.data, format='json')

        # check inventory count
        inventory_count = WareInventory.objects.get(ware=self.ware, warehouse=self.ware.warehouse).count
        self.assertEqual(inventory_count, count)

        # factor 'sale' 3
        self.data["item"]["type"] = 'sale'
        self.data["items"]["items"][0]["count"] = '10'
        if count > int(self.data["items"]["items"][0]["count"]):
            count -= int(self.data["items"]["items"][0]["count"])
        self.client.post(reverse('factor-list'), data=self.data, format='json')

        # check inventory count
        inventory_count = WareInventory.objects.get(ware=self.ware, warehouse=self.ware.warehouse).count
        self.assertEqual(inventory_count, count)

        # factor 'buy' 3
        self.data["item"]["type"] = 'buy'
        self.data["items"]["items"][0]["count"] = '5'
        count += int(self.data["items"]["items"][0]["count"])
        self.client.post(reverse('factor-list'), data=self.data, format='json')

        # check inventory count
        inventory_count = Ware.get_inventory_count(self.ware, self.ware.warehouse)
        self.assertEqual(inventory_count, count)

    def test_factors_with_mean_weighted_ware(self):
        self.ware.pricingType = Ware.WEIGHTED_MEAN
        self.ware.save()

        expected_inventory_count = 0

        # factor 'buy' #1
        count = 5
        fee = 100000
        factor_type = 'buy'
        stat, factor_id = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        # factor 'buy' #2
        count = 7
        fee = 150000
        factor_type = 'buy'
        stat, factor_id = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        # factor 'sale' #1
        count = 4
        fee = 12000
        factor_type = 'sale'
        stat, factor_id = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        # factor 'sale' #2
        count = 5
        fee = 100000
        factor_type = 'sale'
        stat, factor_id = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        # factor 'sale' #3
        count = 10
        fee = 90000
        factor_type = 'sale'
        stat, factor_id = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        # factor 'buy' #3
        count = 6
        fee = 11000
        factor_type = 'buy'
        stat, factor_id = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        inventory_count = self.ware.get_inventory_count(self.ware.warehouse)
        self.assertEqual(expected_inventory_count, inventory_count)

    def test_back_from_buy_and_sale(self):
        self.ware.pricingType = Ware.WEIGHTED_MEAN
        self.ware.save()

        expected_inventory_count = 0

        # factor 'buy' #1
        count = 5
        fee = 100000
        factor_type = 'buy'
        stat, factor_id = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        # factor 'buy' #2
        count = 10
        fee = 150000
        factor_type = 'buy'
        stat, factor_id = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        # factor 'back_from_buy' #1
        count = 4
        fee = 10000
        factor_type = 'backFromBuy'
        stat, factor_id = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        # factor 'sale' #1
        count = 6
        fee = 100000
        factor_type = 'sale'
        stat, factor_id = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        # factor 'sale' #2
        count = 10
        fee = 90000
        factor_type = 'sale'
        stat, factor_id = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        # factor 'back_from_sale' #1
        count = 5
        fee = 120000
        factor_type = 'backFromSale'
        stat, factor_id = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        # factor 'buy' #3
        count = 6
        fee = 11000
        factor_type = 'buy'
        stat, factor_id = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        # factor 'back_from_buy' #2
        count = 8
        fee = 10000
        factor_type = 'backFromBuy'
        stat1, factor_id1 = send_test_factor(self, count, fee, factor_type=factor_type)

        expected_inventory_count = get_expected_inventory_count(factor_type, stat, count, expected_inventory_count)

        inventory_count = self.ware.get_inventory_count(self.ware.warehouse)
        self.assertEqual(expected_inventory_count, inventory_count)
