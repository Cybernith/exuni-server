import datetime
from typing import Any

import jdatetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail
from rest_framework.fields import DateField, DateTimeField

from helpers.functions import date_to_str, datetime_to_str


class JDateField(DateField):
    def to_representation(self, value: Any) -> Any:
        if value:
            return date_to_str(value)
        return ''

    def to_internal_value(self, value):
        if value:
            if isinstance(value, datetime.date):
                return value
            if '-' in value:  # it's gregorian
                return datetime.date(*[int(v) for v in value.split('-')])
            elif '/' in value:  # it's jalali
                return jdatetime.date(*[int(v) for v in value.split('/')]).togregorian()
            else:
                raise ValueError("BAD DATE")
        return None


class JDateTimeField(DateTimeField):
    def to_representation(self, value: Any) -> Any:
        if value:
            return datetime_to_str(value)
        return ''


class SModelSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.name', allow_null=True, allow_blank=True, read_only=True)

    @property
    def serializer_field_mapping(self):
        mapping = super(SModelSerializer, self).serializer_field_mapping
        mapping[models.DateField] = JDateField
        mapping[models.DateTimeField] = JDateTimeField
        return mapping


def validate_required_fields(attrs, required_fields):
    for field in required_fields:
        if not (attrs.get(field) if isinstance(attrs, dict) else getattr(attrs, field)):
            error_body = {field: [ErrorDetail(_("This field is required."), code="required")]}
            raise serializers.ValidationError(error_body)


def DECIMAL_FIELD(**kwargs):
    return serializers.DecimalField(max_digits=24, decimal_places=6, **kwargs)
