from django.contrib.auth.models import Permission
from django.views.generic.base import View
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from helpers.models import BaseModel


def get_codenames(request, view):
    permission_codename = getattr(view, 'permission_codename', None)

    permission_codenames = []
    if permission_codename:
        permission_codenames.append(permission_codename)

        operation = permission_codename.split('.')[0]
        permission_codenames.append(permission_codename.replace(operation, "{}Own".format(operation)))
    else:
        base_codename = getattr(view, 'permission_basename', None)
        if not base_codename:
            raise Exception(
                "permission_basename does not found, declare permission_basename or permission_codename in view"
            )

        method = request.method.upper()

        operations = []
        if method == 'POST':
            operations.append("create")
        if method == 'GET':
            operations.append("get")
            operations.append("getOwn")
        if method in ('PUT', 'PATCH'):
            operations.append("update")
            operations.append("updateOwn")
        if method == 'DELETE':
            operations.append("delete")
            operations.append("deleteOwn")

        for operation in operations:
            permission_codenames.append("{}.{}".format(operation, base_codename))

    if len(permission_codenames) == 0:
        raise Exception("Set Permission On: {}".format(view.__class__))

    return permission_codenames


class BasicObjectPermission(BasePermission):

    def has_object_permission(self, request: Request, view: View, obj: BaseModel) -> bool:
        user = request.user

        if request.method == 'OPTIONS':
            return True

        codenames = get_codenames(request, view)

        if user.has_perm(codenames[0]):
            has_perm = True
        else:
            has_perm = request.user.has_object_perm(obj, codenames[1])

        return has_perm


class BasicCRUDPermission(BasicObjectPermission):

    def has_permission(self, request, view):
        user = request.user

        if request.method == 'OPTIONS':
            return True

        permission_codenames = get_codenames(request, view)

        for permission_codename in permission_codenames:
            has_perm = user.has_perm(permission_codename)
            if has_perm:
                return True

        permission_codename = permission_codenames[0]
        permission = Permission.objects.filter(codename=permission_codename).first()
        if permission:
            self.message = "شما دسترسی این عملیات را ندارید: {}".format(permission.name)
        else:
            self.message = "not found permission: {}".format(permission_codename)

        return False


class TokenAuthSupportQueryString(TokenAuthentication):

    def authenticate(self, request):
        token = request.query_params.get("token", None)

        if token:
            result = self.authenticate_credentials(token)
        else:
            result = super(TokenAuthSupportQueryString, self).authenticate(request)

        return result


class DefinedItemUDPermission(BasePermission):
    """
    Should set permission_basename in view
    """

    def has_object_permission(self, request: Request, view: View, obj: BaseModel) -> bool:
        if request.method.lower() in ('put', 'delete'):
            user = request.user

            has_define_perm = user.has_object_perm(obj, f'define.{view.permission_basename}')
            if has_define_perm:
                return True
            else:
                return False

        return True
