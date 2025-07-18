from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from helpers.functions import get_current_user
from issues.lists.filters import IssueFilter
from issues.models import Issue
from issues.serializers import IssueSerializer, IssueStatusSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class IssueListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = IssueSerializer
    filterset_class = IssueFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Issue.objects.all().order_by('severity')


class AdminOwnIssueListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = IssueSerializer
    filterset_class = IssueFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Issue.objects.filter(created_by=get_current_user())


class OwnAssignedIssueListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = IssueSerializer
    filterset_class = IssueFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Issue.objects.filter(assigned_to=get_current_user())


class IssueStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        issue = get_object_or_404(Issue, pk=pk)
        serializer = IssueStatusSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        issue = serializer.update(issue, serializer.validated_data)
        out_serializer = IssueSerializer(issue, context={'request': request})
        return Response(out_serializer.data, status=status.HTTP_200_OK)
