from django.contrib import admin

# Register your models here.

from common.models import Coordinate, CodeConst


# Register your models here.
@admin.register(CodeConst)
class CodeConstAdmin(admin.ModelAdmin):

    list_display = ('cd', 'cdNm', 'subCd', 'subNm')
    list_per_page = 15

    list_filter = ('cd', 'cdNm', 'subCd', 'subNm')


# Register your models here.
@admin.register(Coordinate)
class CoordinateAdmin(admin.ModelAdmin):

    list_display = ('crdDiv', 'itemNm', 'itemSort', 'crdX', 'crdY', 'defVal', 'cmnt1')
    list_per_page = 15
