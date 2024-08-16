from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from helpers.auth import BasicCRUDPermission


class ToggleItemLockView(APIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission,)
    permission_codename = None
    serializer_class = None

    def post(self, request):
        data = request.data
        item = get_object_or_404(
            self.serializer_class.Meta.model,
            pk=data.get('item')
        )

        if item.is_locked:
            item.unlock()
        else:
            item.lock()

        return Response(self.serializer_class(instance=item).data)

