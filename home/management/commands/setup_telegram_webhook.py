import logging

import requests
from django.conf import settings
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Runs telegram bot through webhook"

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            return

        if not settings.TELEGRAM_BOT_API_SECRET:
            logger.info(
                "Missing 'TELEGRAM_BOT_API_SECRET' in environment variables, prevent setting up webhook"
            )
            return

        webhook_url = "https://api.wits.win/auth/telegram/webhook/"

        telegram_api_url = (
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook"
        )

        try:
            requests.post(
                telegram_api_url,
                data={
                    "url": webhook_url,
                    "secret_token": settings.TELEGRAM_BOT_API_SECRET,
                },
            )

        except requests.RequestException as e:
            logger.info(f"Failed to setup the webhook for telegram bot:\n{e}")
