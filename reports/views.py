from django.http import HttpResponse
from import_export import fields
from import_export import resources
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from helpers.auth import BasicCRUDPermission
from reports.models import ExportVerifier
from reports.serializers import ExportVerifierSerializer
from sanads.models import Sanad


class ModelResource(resources.ModelResource):
    @classmethod
    def field_from_django_field(self, field_name, django_field, readonly):
        FieldWidget = self.widget_from_django_field(django_field)
        widget_kwargs = self.widget_kwargs_for_field(field_name)
        field = fields.Field(attribute=field_name, column_name=django_field.verbose_name,
                             widget=FieldWidget(**widget_kwargs), readonly=readonly)
        return field


class SanadResource(ModelResource):
    class Meta:
        model = Sanad


@api_view(['get'])
def exportTest(request):
    dataset = SanadResource().export()

    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="persons.xls"'
    return response


class ExportVerifiersModelView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, BasicCRUDPermission,)
    permission_basename = 'exportVerifier'
    serializer_class = ExportVerifierSerializer

    def get_queryset(self):
        return ExportVerifier.objects.inFinancialYear().all()

    def perform_create(self, serializer: ExportVerifierSerializer) -> None:
        serializer.save(financial_year=self.request.user.active_financial_year)
