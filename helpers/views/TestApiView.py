import json

from bson import json_util
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from server.configs import RequestLogs

class TestApiView(APIView):

    def post(self, request):
        return Response([])

    def get(self, request):
        return Response([])
