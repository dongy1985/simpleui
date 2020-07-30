import time
import calendar
import os
import zipfile

from django.contrib import admin, messages
from django.db import transaction
from django.shortcuts import render
from django.contrib.admin import actions
from django.urls import reverse
from django.contrib import admin

# Register your models here.
from aggregation.models import Aggregation
from django.contrib.auth import get_permission_codename
from django.db.models import Q
from django.contrib.auth import get_user
from django.http.response import HttpResponse
from django.http import HttpResponse

from attendance.models import *
from aggregation.models import *
from common.models import *
from company.models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from common.custom_filter import DateFieldFilter
from common import mailUtil
from common import excelUtil
from common import outPutFile
from common.const import const


@admin.register(Aggregation)
class AggregationAdmin(admin.ModelAdmin):
    actions = ['export_button', ]
    # display
    list_display = (
        'name', 'empNo', 'attendance_YM', 'working_time', 'attendance_count', 'absence_count', 'annual_leave',
        'rest_count',
        'late_count')
    # set search
    search_fields = ('empNo', 'name', 'attendance_YM')
    # list
    list_filter = (('attendance_YM', DateFieldFilter),)
    ordering = ('attendance_YM', 'empNo', 'name')
    list_per_page = 7

    # excle導出
    def export_button(self, request, queryset):
        # mkDir
        folder_name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        if os.path.isdir(const.DIR):
            os.mkdir(os.path.join(const.DIR, folder_name))
        # 获取表单数据
        datFrom = request.GET.get('attendance_YM__gte')[0:7]
        datTo = request.GET.get('attendance_YM__lt')[0:7]
        if datFrom == datTo:
            # 月度単位の集計表(excel)の導出
            excelUtil.exportExcel(queryset, folder_name, datFrom)
            messages.add_message(request, messages.SUCCESS, 'SUCCESS')
        else:
            # 年度単位の集計表(excel)の導出
            count = 0
            fileName = ""
            outPutFile.export(queryset, folder_name, fileName, count)
            messages.add_message(request, messages.SUCCESS, 'SUCCESS')

    export_button.short_description = ' 導出'
    export_button.type = 'primary'
    export_button.icon = 'el-icon-document-copy'
    export_button.allowed_permissions = ('export_button_aggregation',)

    def has_export_button_aggregation_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('export_button', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))
