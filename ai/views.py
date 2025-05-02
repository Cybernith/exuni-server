from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.models import ChatMessage
from ai.throttles import UserChatGPTThrottle, AnonChatGPTThrottle, DeleteSearchHistoryRateThrottle
from ai.utils import ChatGPTClient

import openai


class ChatGPTAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserChatGPTThrottle, AnonChatGPTThrottle]

    def post(self, request):
        message = request.data.get("message")
        if not message:
            return Response({"error": "message is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None
        try:
            client = ChatGPTClient(user=user, model="gpt-3.5-turbo")
            response = client.ask(message)
            return Response({"response": response})
        except Exception as exception:
            return Response({"error": str(exception)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteSearchHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [DeleteSearchHistoryRateThrottle]

    def delete(self, request):
        deleted_count, _ = ChatMessage.objects.filter(user=request.user).delete()
        return Response(
            {"message": f"{deleted_count} مورد از تاریخچه سرچ شما حذف شد."}, status=status.HTTP_200_OK)


