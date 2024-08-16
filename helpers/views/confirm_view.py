from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from helpers.auth import BasicCRUDPermission


class ConfirmView(APIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission,)
    permission_basename = None
    model = None

    @property
    def permission_codename(self):
        if self.model is None:
            raise Exception("Set model in Confirm View")
        if self.permission_basename is None:
            raise Exception("Set permission_basename in Confirm View")
        instance = self.get_object()
        if not instance.has_first_confirmation:
            return 'firstConfirm.{}'.format(self.permission_basename)
        else:
            return 'secondConfirm.{}'.format(self.permission_basename)

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs.get('pk'))

    def put(self, request, **kwargs):
        instance = self.get_object()
        cancel = request.data.get('cancel', False)
        if instance.can_confirm():
            if cancel:
                instance.cancelConfirm()
            else:
                instance.confirm()
        return Response([])
