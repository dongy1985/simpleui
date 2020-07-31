import os
from company.models import *
from common import fileUtil
from common.const import const
from django.contrib.auth import get_permission_codename
from django.contrib import messages
from django.contrib import admin
from attendanceStatistics.models import AttendanceStatistics
from common.custom_filter import DateFieldFilter


@admin.register(AttendanceStatistics)
class AttendanceStatisticsAdmin(admin.ModelAdmin):
    list_display = (
    'empNo', 'name', 'attendance_YM', 'working_time', 'attendance_count', 'absence_count', 'annual_leave', 'rest_count',
    'late_count')
    list_per_page = 7
    search_fields = ('empNo', 'name', 'attendance_YM')
    list_filter = (('attendance_YM', DateFieldFilter),)
    ordering = ('attendance_YM', 'name')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

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