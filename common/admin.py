from django.contrib import admin

# Register your models here.

from common.models import Coordinate, CodeConst


# Register your models here.
@admin.register(CodeConst)
# class RecordAdmin(admin.ModelAdmin):
# class RecordAdmin(ImportExportModelAdmin):
class CodeConstAdmin(admin.ModelAdmin):

    list_display = ('big_code', 'big_name', 'small_code', 'small_name')
    list_per_page = 15

    list_filter = ('big_code', 'big_name', 'small_code', 'small_name')


# Register your models here.
@admin.register(Coordinate)
# class RecordAdmin(admin.ModelAdmin):
# class RecordAdmin(ImportExportModelAdmin):
class CoordinateAdmin(admin.ModelAdmin):

    list_display = ('coorDivision', 'dspOrder', 'coorName', 'coorX', 'coorY', 'fixedValue', 'remarks')
    list_per_page = 15
