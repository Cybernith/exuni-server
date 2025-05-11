import binascii
import os
from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import F
from woocommerce import API

from users.models import User
import json


class Command(BaseCommand):
    help = 'retrieve customers from orders'

    def handle(self, *args, **options):
        User.objects.filter(user_type=User.CUSTOMER).delete()
        wcapi = API(
            url="https://exuni.ir",
            consumer_key="ck_7df59e4d651a9449c675f453ea627481f13a4690",
            consumer_secret="cs_c1a783a3d1bbe9b3d552119fa174dc84824f5c64",
            version="wc/v3",
            wp_api=True,
            timeout=30
        )
        page = 36775
        response_len = 2
        while response_len == 2:
            response = wcapi.get("orders", params={"per_page": 2, 'page': page}).json()
            for user in response:
                user_data = {
                    'user_type': User.CUSTOMER,
                    'username': user['billing']['phone'] or binascii.hexlify(os.urandom(15)).decode(),
                    'mobile_number': user['billing']['phone'],
                    'first_name': user['billing']['first_name'],
                    'last_name': user['billing']['last_name'],
                    'address': user['billing']['address_1'],
                    'postal_code': user['billing']['postcode'],
                    'state': user['billing']['state'],
                    'city': user['billing']['city'],
                    'email': user['billing']['email'],
                }
                file_name = 'order_customer.json'
                with open(file_name, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                data.append(user_data)
                with open(file_name, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
            print(f'{2 * page} user retrieved')
            page += 1
            response_len = len(response)

            # users = [User(**item) for item in users_list]
            # User.objects.bulk_create(users)





