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
from common import fileUtil
from common import outPutFile
from common.const import const


@admin.register(Aggregation)
class AggregationAdmin(admin.ModelAdmin):
    actions = ['export_button', ]
    # display
    list_display = ('empNo', 'name', 'attendance_YM', 'working_time', 'attendance_count', 'absence_count', 'annual_leave', 'rest_count', 'late_count')
    # set search
    search_fields = ('empNo', 'name', 'attendance_YM')
    # list
    list_filter = (('attendance_YM', DateFieldFilter),)
    ordering = ('attendance_YM', 'empNo', 'name')
    list_per_page = 7

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = ['empNo', 'name', 'attendance_YM', 'working_time', 'attendance_count', 'absence_count', 'annual_leave', 'rest_count', 'late_count']
        return self.readonly_fields

    # excle導出
    def export_button(self, request, queryset):
        # mkDir
        folder_name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        if os.path.isdir(const.DIR):
            os.mkdir(os.path.join(const.DIR, folder_name))
        # 統計年月開始を取得
        attendance_YM_From = request.GET.get('attendance_YM__gte')[0:7]
        # 統計年月終了を取得
        attendance_YM_To = request.GET.get('attendance_YM__lt')[0:7]
        # 月度単位または年度単位の判断
        if attendance_YM_From == attendance_YM_To:
            # 月度単位の集計表(excel)の導出
            fileUtil.exportExcel(folder_name, attendance_YM_From)
            messages.add_message(request, messages.SUCCESS, 'SUCCESS')
        else:
            # 年度単位の集計表(excel)の導出
            fileUtil.exportYearExcel(folder_name, attendance_YM_From, attendance_YM_To)
            messages.add_message(request, messages.SUCCESS, 'SUCCESS')

    export_button.short_description = ' 導出'
    export_button.type = 'primary'
    export_button.icon = 'el-icon-document-copy'
    export_button.allowed_permissions = ('export_button_aggregation',)

    def has_export_button_aggregation_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('export_button', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))
