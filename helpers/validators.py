from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


class ModelValidator:
    phone_validator = RegexValidator(regex='^(09){1}[0-9]{9}$', message=_('phone number format: 09*********'))

    @staticmethod
    def file_validator(value, max_size, extensions):
        import os
        ext = os.path.splitext(value.name)[1]
        if ext.lower() not in extensions:
            raise ValidationError(_('extension is not supported'))
        if value.size > max_size:
            raise ValidationError(_('size must be lower than 500 Kb'))

    @staticmethod
    def image_validator(value):
        ModelValidator.file_validator(value, 500 * 1024, ['.jpg', '.png', '.jpeg'])

    @staticmethod
    def attachment_validator(value):
        ModelValidator.file_validator(value, 3 * 1024 * 1024, ['.zip', '.pdf'])

    @staticmethod
    def day_of_month_validator(value):
        if value < 1 or value > 30:
            raise ValidationError(_('day must be between 1 and 30'))
