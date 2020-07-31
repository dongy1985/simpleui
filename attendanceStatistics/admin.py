from django.contrib import admin
from attendanceStatistics.models import AttendanceStatistics
from common.custom_filter import DateFieldFilter


@admin.register(AttendanceStatistics)
class AttendanceStatisticsAdmin(admin.ModelAdmin):
    list_display = (
    'empNo', 'name', 'attendance_YM', 'working_time', 'attendance_count', 'absence_count', 'annual_leave', 'rest_count',
    'late_count')
    list_per_page = 7
    list_filter = (('attendance_YM', DateFieldFilter),)
    ordering = ('attendance_YM', 'name')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
