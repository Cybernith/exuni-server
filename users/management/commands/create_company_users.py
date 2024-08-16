from django.core.management.base import BaseCommand
from companies.models import Company, CompanyUser
from helpers.test import set_user


class Command(BaseCommand):
    help = 'Create company users for old companies'

    def handle(self, *args, **options):
        for company in Company.objects.all():
            superuser = company.superuser

            set_user(superuser)

            if not company.created_by:
                company.created_by = superuser
            company.modules = superuser.modules
            company.save()

            financial_years = company.financial_years.all()
            users = list(superuser.users.all())
            users.append(superuser)
            for user in users:
                obj, created = CompanyUser.objects.get_or_create(
                    company=company,
                    user=user,
                )
                obj.financialYears.set(financial_years)
                obj.roles.set(user.roles.all())
