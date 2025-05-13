from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import F
from woocommerce import API

from server.settings import WC_C_KEY, WC_C_SECRET
from users.models import User
import json


class Command(BaseCommand):
    help = 'retrieve customers'

    def handle(self, *args, **options):
        User.objects.filter(user_type=User.CUSTOMER).delete()
        wcapi = API(
            url="https://exuni.ir",
            consumer_key=WC_C_KEY,
            consumer_secret=WC_C_SECRET,
            version="wc/v3",
            wp_api=True,
            timeout=30
        )
        page = 391
        response_len = 50
        while response_len == 50:
            response = wcapi.get("customers", params={"per_page": 50, 'page': page}).json()
            for user in response:
                user_data = {
                    'user_type': User.CUSTOMER,
                    'username': user['billing']['phone'] or user['username'] or user['email'],
                    'mobile_number': user['billing']['phone'],
                    'first_name': user['billing']['first_name'],
                    'last_name': user['billing']['last_name'],
                    'address': user['billing']['address_1'],
                    'postal_code': user['billing']['postcode'],
                    'state': user['billing']['state'],
                    'city': user['billing']['city'],
                    'email': user['email'] or user['billing']['email'],
                }
                file_name = 'customers.json'
                with open(file_name, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                data.append(user_data)
                with open(file_name, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
            print(f'{50 * page} user retrieved')
            page += 1
            response_len = len(response)

            # users = [User(**item) for item in users_list]
            # User.objects.bulk_create(users)





