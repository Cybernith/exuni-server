from decimal import Decimal

from django.contrib.admin.options import get_content_type_for_model

from accounts.defaultAccounts.models import DefaultAccount
from companies.models import FinancialYear
from helpers.functions import get_object_accounts
from helpers.models import BaseModel
from sanads.models import Sanad, newSanadCode, clearSanad


class AutoSanad:
    """
        How to use:
         1. Inherit from this class
         2. Implement

        IMPORTANT NOTE: Don't call update method in `Model.save` method
    """

    def __init__(self, instance):
        self.instance = instance

    def get_sanad_date(self):
        return self.instance.date

    def get_sanad_explanation(self):
        return self.instance.explanation

    def get_sanad_rows(self, instance: BaseModel) -> list:
        raise NotImplementedError()

    def update(self, is_confirmed=True):
        sanad = self._get_sanad()

        rows = self.get_sanad_rows(self.instance)
        self.create_sanad_items(sanad, rows)
        sanad.update_values(order_items=True)

        if not is_confirmed:
            sanad.check_account_balance_confirmations()

        self.instance.sanad = sanad
        self.instance.save()

    def _get_sanad(self) -> Sanad:
        sanad = self.instance.sanad
        if not sanad:

            sanad = Sanad.objects.create(
                code=newSanadCode(),
                financial_year=self.instance.financial_year,
                is_auto_created=True,
                origin_content_type=get_content_type_for_model(type(self.instance)),
                origin_id=self.instance.id,

                date=self.get_sanad_date(),
                explanation=self.get_sanad_explanation(),
            )
            self.instance.sanad = sanad
            self.instance.save()
        else:
            sanad.delete_items(self.instance)
            sanad.date = self.get_sanad_date()
            sanad.explanation = self.get_sanad_explanation()
            sanad.origin_content_type = get_content_type_for_model(type(self.instance))
            sanad.origin_id = self.instance.id
            sanad.save()

        sanad.define()

        return sanad

    @staticmethod
    def create_sanad_items(sanad: Sanad, sanad_items: list):
        """
        :param sanad: Sanad
        :param sanad_items: array[{any field of SanadItem}, ...]
        # You can pass default accounts as string!
        :return: None
        """

        for sanad_item in sanad_items:
            if isinstance(sanad_item['account'], str):
                sanad_item.update(get_object_accounts(DefaultAccount.get(sanad_item['account'])))

            sanad_item['bed'] = sanad_item.get('bed', 0)
            sanad_item['bes'] = sanad_item.get('bes', 0)

            sanad_item['origin_content_type'] = sanad_item.get('origin_content_type', sanad.origin_content_type)
            sanad_item['origin_id'] = sanad_item.get('origin_id', sanad.origin_id)

        for sanad_item in sanad_items:
            if sanad_item['bed'] == sanad_item['bes'] == 0:
                continue

            sanad.items.create(
                **sanad_item
            )

    def merge_items(self, rows, explanation='', **kwargs):
        """
        merges multiple items based on kwargs into one item with one bed or bes
        usually kwargs are account + floats
        """
        merged_items = []
        bed = 0

        for row in rows:
            do_merge = True
            for key, value in kwargs.items():
                if row[key] != value:
                    do_merge = False
                    merged_items.append(row)
                    break

            if do_merge:
                bed += row.get('bed', Decimal(0)) - row.get('bes', Decimal(0))

        merged_items.append({
            **kwargs,
            'explanation': explanation,
            'bed' if bed > 0 else 'bes': abs(bed)
        })
        return merged_items
