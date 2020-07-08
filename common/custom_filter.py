from django.contrib import admin
from django import template

register = template.Library()


@register.filter(name='DateFieldFilter')
class DateFieldFilter(admin.filters.DateFieldListFilter):
    def __init__(self, *args, **kwargs):
        if args and len(args) > 2 and args[2]:
            fieldNm = kwargs['field_path']
            args[2][fieldNm + '__lte'] = args[2].pop(fieldNm + '__lt')
        super(DateFieldFilter, self).__init__(*args, **kwargs)
