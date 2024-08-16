import os
import webbrowser

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Roll database back to current existing migrations'

    def handle(self, *args, **options):
        print(self.get_last_migrations())

    def get_last_migrations(self):
        for directory in os.listdir():
            path = f"{directory}/migrations"
            if os.path.isdir(path):
                os.chdir(path)
                last_migration = [migration for migration in os.listdir() if migration.endswith(".py") and migration.startswith('0')][-1].split('.')[0]
                print(directory, last_migration)
                os.chdir("../..")
                call_command('migrate', directory, last_migration)
