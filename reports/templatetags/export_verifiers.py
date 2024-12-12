from django import template

register = template.Library()


@register.inclusion_tag('reports/export_verifiers.html')
def show_verifiers(form, user):
    pass
