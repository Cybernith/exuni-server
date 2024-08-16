from django.urls import reverse
from rest_framework import status


def send_test_factor(self, count, fee, factor_type='buy'):
    self.data["item"]["type"] = factor_type
    self.data["items"]["items"][0]["fee"] = fee
    self.data["items"]["items"][0]["count"] = count
    self.data["items"]["items"][0]["unit_count"] = count

    response = self.client.post(reverse('factor-list'), data=self.data, format='json')
    if response.status_code == status.HTTP_200_OK:
        return response.status_code, response.json().get('id')
    else:
        return response.status_code, None


def get_expected_inventory_count(factor_type, stat, count, prev_count):
    if stat == status.HTTP_200_OK:
        if factor_type == 'buy':
            return prev_count + count
        elif factor_type == 'sale':
            return prev_count - count
        elif factor_type == 'backFromBuy':
            return prev_count - count
        elif factor_type == 'backFromSale':
            return prev_count + count
    return prev_count
