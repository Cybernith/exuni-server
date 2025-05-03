from decimal import Decimal

from rest_framework.response import Response

from financial_management.serivces.wallet_top_up import WalletTopUpService, WalletTopUpRequestService
from financial_management.serivces.wallet_transfer_systhem import WalletTransferService


def top_up_wallet_request(request, amount=None):
    service = WalletTopUpRequestService(
        user=request.user,
        amount=amount or Decimal(request.data["amount"]),
        ip=request.META["REMOTE_ADDR"],
        agent=request.META.get("HTTP_USER_AGENT")
    )
    return Response({"message": service.execute()})


def top_up_wallet(request, amount=None):
    service = WalletTopUpService(
        user=request.user,
        amount=amount or Decimal(request.data["amount"]),
        ip=request.META["REMOTE_ADDR"],
        agent=request.META.get("HTTP_USER_AGENT")
    )
    return Response({"transaction_id": service.execute().id})


def wallet_transfer(request, amount=None, receiver_user=None):
    service = WalletTransferService(
        sender_user=request.user,
        receiver_user=receiver_user,
        amount=amount or Decimal(request.data["amount"]),
        ip=request.META["REMOTE_ADDR"],
        agent=request.META.get("HTTP_USER_AGENT")
    )
    return Response({"transaction_id": service.execute().id})
