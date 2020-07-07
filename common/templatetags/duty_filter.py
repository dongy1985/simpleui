from django.contrib import admin
from django import template

register = template.Library()


@register.filter(name='DutyDateFieldFilter')
class DutyDateFieldFilter(admin.filters.DateFieldListFilter):
    def __int__(self, *args, **kwargs):
        if args and len(args) > 2 and args[2]:
            fieldNm = kwargs['field_path']
            args[2][fieldNm + '__lte'] = args[2].pop(fieldNm + '__lt')
        super(DutyDateFieldFilter, self).__init__(*args, **kwargs)
