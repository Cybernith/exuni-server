from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from helpers.functions import get_current_user
from rest_framework.decorators import api_view, permission_classes

from django.shortcuts import get_object_or_404

from issues.models import Issue
from issues.serializers import IssueCreateSerializer


class IssueCreateAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Issue.objects.all()
    serializer_class = IssueCreateSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=get_current_user())


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_to_self(request, pk):
    issue = get_object_or_404(Issue, pk=pk)

    if not issue.status != Issue.NEW or issue.assigned_to:
        return Response(
            {"detail": "Issue is Assigned"},
            status=status.HTTP_400_BAD_REQUEST
        )
    issue.assigned_to = get_current_user()
    issue.change_status(new_status=Issue.IN_PROGRESS, user=get_current_user())
    issue.save()

    return Response(
        {
            "detail": "Issue assigned to you successfully.",
            "issue": {
                "id": issue.id,
                "title": issue.title,
                "assigned_to": request.user.username
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_done(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    if not issue.created_by == get_current_user():
        return Response(
            {"detail": "Issue is not For You"},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not issue.status != Issue.DONE:
        return Response(
            {"detail": "Issue is not Done Yet"},
            status=status.HTTP_400_BAD_REQUEST
        )
    issue.is_tested = True
    issue.save()

    return Response(
        {
            "detail": "Issue tested successfully.",
            "issue": {
                "id": issue.id,
                "title": issue.title,
                "assigned_to": request.user.username
            }
        },
        status=status.HTTP_200_OK
    )

