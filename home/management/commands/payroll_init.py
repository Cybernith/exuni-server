
from django.core.management.base import BaseCommand

from payroll.models import MinDayPayment, WorkshopTax, WorkshopTaxRow


class Command(BaseCommand):
    help = 'create payroll basic things'

    def handle(self, *args, **options):
        for min_day_payment in MinDayPayment.objects.all():
            min_day_payment.delete()

        for tax in WorkshopTax.objects.all():
            tax.delete()

        MinDayPayment.objects.create(
            from_date='2022-03-21',
            to_date='2023-03-20',
            amount=1393250,
            min_paye_sanavt=70000,
            min_hagh_maskan=6500000,
            min_bon_kharobar=8500000,
            min_hagh_taahol=0,
        )
        MinDayPayment.objects.create(
            from_date='2023-03-21',
            to_date='2024-03-19',
            amount=1769428,
            min_paye_sanavt=70000,
            min_hagh_maskan=9000000,
            min_bon_kharobar=11000000,
            min_hagh_taahol=0,
        )
        MinDayPayment.objects.create(
            from_date='2024-03-20',
            to_date='2025-03-20',
            amount=2388728,
            min_paye_sanavt=70000,
            min_hagh_maskan=9000000,
            min_bon_kharobar=14000000,
            min_hagh_taahol=5000000,
        )

        tax_1401 = WorkshopTax.objects.create(
            name='جدول معافیت مالیاتی 1401',
            from_date='2022-03-21',
            to_date='2023-03-20',
            is_verified=True
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1401,
            from_amount=0,
            to_amount=672000000,
            ratio=0,
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1401,
            from_amount=672000001,
            to_amount=1800000000,
            ratio=10,
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1401,
            from_amount=1800000001,
            to_amount=3000000000,
            ratio=15,
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1401,
            from_amount=3000000001,
            to_amount=4200000000,
            ratio=20,
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1401,
            from_amount=4200000001,
            to_amount=0,
            ratio=30,
            is_last=True
        )
        tax_1402 = WorkshopTax.objects.create(
            name='جدول معافیت مالیاتی 1402',
            from_date='2023-03-21',
            to_date='2024-03-19',
            is_verified=True
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1402,
            from_amount=0,
            to_amount=1200000000,
            ratio=0,
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1402,
            from_amount=1200000001,
            to_amount=1680000000,
            ratio=10,
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1402,
            from_amount=1680000001,
            to_amount=2760000000,
            ratio=15,
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1402,
            from_amount=2760000001,
            to_amount=4080000000,
            ratio=20,
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1402,
            from_amount=4080000001,
            to_amount=0,
            ratio=30,
            is_last=True
        )

        tax_1403 = WorkshopTax.objects.create(
            name='جدول معافیت مالیاتی 1403',
            from_date='2024-03-20',
            to_date='2025-03-20',
            is_verified=True
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1403,
            from_amount=0,
            to_amount=1440000000,
            ratio=0,
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1403,
            from_amount=1440000001,
            to_amount=1980000000,
            ratio=10,
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1403,
            from_amount=1980000001,
            to_amount=3240000000,
            ratio=15,
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1403,
            from_amount=3240000001,
            to_amount=4800000000,
            ratio=20,
        )
        WorkshopTaxRow.objects.create(
            workshop_tax=tax_1403,
            from_amount=4800000001,
            to_amount=0,
            ratio=30,
            is_last=True
        )


