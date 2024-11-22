import datetime

from django.core.management.base import BaseCommand, CommandParser

from accounts.accounts.models import AccountBalance
from companies.models import Company
from helpers.db import queryset_iterator
from helpers.functions import get_object_accounts
from helpers.middlewares.modify_request_middleware import ModifyRequestMiddleware
from sanads.models import SanadItem
from server.settings import BASE_DIR
from subscription.constants import *
from subscription.models import Plan, Extension
from users.models import User
import os


class Command(BaseCommand):
    help = 'Initialize Subscription Module'

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        modules = ','.join([SANADS, TRANSACTIONS, FACTORS, WAREHOUSES])
        extra_user_prices = {
            0: 1_500_000,
        }
        plans = [
            {
                'pk': 1,
                'title': 'بسته پایه',
                'prices': {
                    30: 2_750_000,
                    180: 14_520_000,
                    364: 24_750_000
                },
                'extra_user_prices': extra_user_prices,
                'users_count': 1,
                'modules': modules,
                'features': ','.join([INCOME_STATEMENT_REPORT])
            },
            {
                'pk': 2,
                'title': 'بسته پیشرفته',
                'prices': {
                    30: 4_250_000,
                    180: 22_440_000,
                    364: 38_250_000
                },
                'extra_user_prices': extra_user_prices,
                'users_count': 1,
                'modules': modules,
                'features': ','.join([
                    ACCOUNTS_CUD,
                    UNLIMITED_SIDE_ACCOUNT,
                    UPDATE_ACCOUNT_IN_TREE,
                    BANK_TRANSFER_TRANSACTION,
                    PERMANENT_FINANCIAL_YEAR,
                    FIFO_INVENTORY,
                    UNLIMITED_WAREHOUSE,
                    RECEIPT_AND_REMITTANCE,
                    FACTOR_VISITOR,
                    FACTOR_EXPENSES,
                    CONSUMPTION_WARE_FACTOR,
                    JOURNAL_REPORT,
                    INCOME_STATEMENT_REPORT,
                    DETAILED_INCOME_STATEMENT_REPORT,
                ])
            },
            {
                'pk': 3,
                'title': 'بسته حرفه ای',
                'prices': {
                    30: 7_000_000,
                    180: 36_960_000,
                    364: 63_000_000
                },
                'extra_user_prices': extra_user_prices,
                'users_count': 2,
                'modules': modules,
                'features': ','.join([
                    ACCOUNTS_CUD,
                    UNLIMITED_SIDE_ACCOUNT,
                    UPDATE_ACCOUNT_IN_TREE,
                    FLOAT_ACCOUNTS,
                    BANK_TRANSFER_TRANSACTION,
                    GUARANTEE_DOCUMENTS,
                    IMPREST_TRANSACTION,
                    PERMANENT_FINANCIAL_YEAR,
                    FIFO_INVENTORY,
                    UNLIMITED_WAREHOUSE,
                    RECEIPT_AND_REMITTANCE,
                    FACTOR_VISITOR,
                    FACTOR_EXPENSES,
                    CONSUMPTION_WARE_FACTOR,
                    JOURNAL_REPORT,
                    INCOME_STATEMENT_REPORT,
                    DETAILED_INCOME_STATEMENT_REPORT,
                ])
            },
            {
                'pk': 4,
                'title': 'منابع انسانی',
                'prices': {
                    30: 0,
                    180: 0,
                    364: 0
                },
                'extra_user_prices': extra_user_prices,
                'users_count': 1,
                'modules': [],
                'features': []
            }
        ]

        extensions = [
            {
                'pk': 1,
                'title': 'منابع انسانی',
                'prices': {
                    30: 3_000_000,
                    180: 15_840_000,
                    364: 27_000_000,
                    'extra_workshop': 10_000_000  # for 360 days by default
                },
                'options': {
                    'workshops_count': 1
                }
            }
        ]

        for plan in plans:
            Plan.objects.update_or_create(pk=plan['pk'], defaults=plan)

        for extension in extensions:
            extension, _ = Extension.objects.update_or_create(pk=extension['pk'], defaults=extension)

        # for company in Company.objects.all():
        #     company.plan_id = plans[2]['pk']
        #     company.modules = plans[2]['modules']
        #     company.features = plans[2]['features']
        #     company.extensions.add(1)
        #     company.options = extension.options
        #     company.save()
