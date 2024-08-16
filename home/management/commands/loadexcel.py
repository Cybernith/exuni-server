import json
from pprint import pprint

import pandas as pd
from django.apps import apps
from django.core.management import CommandParser
from django.core.management.base import BaseCommand
from django.db.models import Q

from companies.models import FinancialYear
from distributions.models import Path
from factors.factor_sanad import FactorSanad
from factors.models import Factor
from helpers.test import set_user
from home.models import DefaultText
from server.settings import BASE_DIR
from users.models import User


class Command(BaseCommand):
    help = 'Load data from excel'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **options):

        file_path = options['file_path']
        data = pd.read_excel(file_path, sheet_name=None, skiprows=1)['Transformed by JSON-CSV.CO'].to_dict()

        user = User.objects.get(pk=data.pop('user')[0])
        set_user(user)

        financial_year = FinancialYear.objects.get(pk=data.pop('financial_year')[0])

        app_label = data.pop('app_label')[0]
        model_name = data.pop('model_name')[0]
        Model = apps.get_model(app_label, model_name)

        id_map = {}

        items_count = len(data['id'])
        fields = list(data.keys())
        fields.pop(0)
        for i in range(items_count):

            item_data = {}
            local_id = int(data['id'][i])
            for field in fields:
                value = data[field][i]

                # Check nan values
                if value != value:
                    value = None
                # Replace parent id with db id
                elif field == 'parent_id':
                    value = id_map[int(value)]

                item_data[field] = value

            item = Model.objects.create(
                financial_year=financial_year,
                **item_data
            )
            id_map[local_id] = item.id

        print(id_map)
