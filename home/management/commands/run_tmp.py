import csv
import json

import pandas as pd
from django.contrib.admin.options import get_content_type_for_model
from django.core.management import CommandParser
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.db.models import Q

from accounts.accounts.models import Account, AccountType
from accounts.defaultAccounts.models import DefaultAccount, BaseDefaultAccount
from cheques.models.ChequeModel import Cheque
from cheques.models.StatusChangeModel import StatusChange
from companies.models import Company, FinancialYear, CompanyUser
from factors.models import Factor, Transfer
from helpers.middlewares.modify_request_middleware import ModifyRequestMiddleware
from helpers.querysets import delete_object_recursively
from helpers.test import set_user
from imprests.models import ImprestSettlement
from sanads.models import Sanad, SanadItem
from server.settings import BASE_DIR
from transactions.models import Transaction
from users.models import User


class Command(BaseCommand):
    help = 'Tmp command, for testing, correcting, bug fixing and etc'

    def add_arguments(self, parser: CommandParser) -> None:
        # parser.add_argument('financial_year_id', type=int)
        pass

    def handle(self, *args, **options):
        file_path = f'{BASE_DIR}/accounts/coding.xlsx'
        data = pd.read_excel(file_path, sheet_name='نوع ها و ماهیت', skiprows=1).values
        print(data)

        for row in data:
            name = row[1]

            nature = row[2]
            if nature == 'بدهکار':
                nature = 'bed'
            elif nature == 'بستانکار':
                nature = 'bes'
            elif nature == 'خنثی':
                nature = 'non'
            else:
                raise Exception(f"Bad nature in account types: {nature}")

            usage = row[3]
            if usage == 'سود و زیان':
                usage = AccountType.INCOME_STATEMENT
            elif usage == 'ترازنامه':
                usage = AccountType.BALANCE_SHEET
            else:
                usage = AccountType.NONE

            AccountType.objects.update_or_create(
                name=name,
                defaults={
                    'nature': nature,
                    'usage': usage
                }
            )

    def add_base_default_accounts(self):
        names = [
            'پیش فرض حساب های انتظامی -چک واگذار شده'
            ,'پیش فرض حساب های انتظامی - سفته واگذار شده'
            ,'پیش فرض حساب های انتظامی - ضمانتنامه واگذار شده'
            ,'پیش فرض حساب های انتظامی - چک اخذ شده'
            ,'پیش فرض حساب های انتظامی - سفته اخذ شده'
            ,'پیش فرض حساب های انتظامی - ضمانتنامه اخذ شده'
            ,'پیش فرض طرف حساب های انتظامی -چک واگذار شده'
            ,'پیش فرض طرف حساب های انتظامی - سفته واگذار شده'
            ,'پیش فرض طرف حساب های انتظامی - ضمانتنامه واگذار شده'
            ,'پیش فرض طرف حساب های انتظامی - چک اخذ شده'
            ,'پیش فرض طرف حساب های انتظامی - سفته اخذ شده'
            ,'پیش فرض طرف حساب های انتظامی - ضمانتنامه اخذ شده'
        ]

        codenames = [
            'transferredGuaranteeCheque',
            'transferredGuaranteePromissoryNote',
            'transferredBankGuarantee',
            'receivedGuaranteeCheque',
            'receivedGuaranteePromissoryNote',
            'receivedBankGuarantee',
            'transferredGuaranteeChequeParty',
            'transferredGuaranteePromissoryNoteParty',
            'transferredBankGuaranteeParty',
            'receivedGuaranteeChequeParty',
            'receivedGuaranteePromissoryNoteParty',
            'receivedBankGuaranteeParty',
        ]

        for i in range(len(names)):
            name = names[i]
            codename = codenames[i]

            BaseDefaultAccount.objects.create(
                name=name,
                codename=codename,
                usage=BaseDefaultAccount.GUARANTEE,
                account_level=Account.TAFSILI,
            )

    def delete_companies(self, company_ids):
        length = len(company_ids)
        for company_id in company_ids:
            print(length)
            company = Company.objects.filter(pk=company_id).first()
            if company:
                delete_object_recursively(company)
            length -= 1

    @staticmethod
    def find_bad_sanads(financial_year_id):
        for sanad_item in SanadItem.objects.filter(financial_year_id=financial_year_id).all():
            for i in range(1, 5):
                if getattr(sanad_item.account, f'floatAccount{i}Groups').count() > 0:
                    if not getattr(sanad_item, f'floatAccount{i}'):
                        print(sanad_item.sanad.code)
