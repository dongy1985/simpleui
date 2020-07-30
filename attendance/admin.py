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
from django.contrib.auth import get_user
from django.http.response import HttpResponse
from django.http import HttpResponse
from django.contrib.auth import get_permission_codename
from django.db.models import Q
from wsgiref.util import FileWrapper
from datetime import date, timedelta

from attendance.models import *
from common.models import *
from company.models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from common.custom_filter import DateFieldFilter
from common import fileUtil
from common import mailUtil
from common.const import const

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    actions = ['cancel_button', 'commit_button', 'confirm_button', 'export', ]
    #admin.site.disable_action('delete_selected')
    #display
    list_display = ('name', 'date', 'duty', 'start_time', 'end_time', 'rest', 'working_time', 'contents', 'status')
    #list
    list_filter = ('status',('date', DateFieldFilter))
    #set search
    search_fields = ('name',)
    #set field
    fieldsets = [(None,{'fields':['date', 'duty', 'start_time', 'end_time', 'rest', 'contents']})]
    ordering = ( 'name', 'date')
    list_per_page = 7

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.status != const.WORK_TYPE_SMALL_0:  
                return False
        return super().has_delete_permission(request)

    #user set
    def save_model(self, request, obj, form, change):
        if obj.status != const.WORK_TYPE_SMALL_0:
            messages.add_message(request, messages.ERROR, '提出済记录が編集できません')
            return
        # 名前、ＩＤ
        if obj.user_id == const.DEF_USERID:
            obj.user_id = request.user.id
            obj.name = Employee.objects.get(user=request.user.id).name
        # 実働時間计算
        end_time = datetime.strptime(str(obj.end_time),"%H:%M:%S")
        sumTime1 = end_time - timedelta(hours=obj.start_time.hour,minutes=obj.start_time.minute,seconds=obj.start_time.second)
        sum_hour = sumTime1.hour
        sum_minute = sumTime1.minute
        if sum_minute != 0:
            sum_hour_dcm = sum_minute / 60
        else:
            sum_hour_dcm = 0
        sumTime2 = sum_hour + sum_hour_dcm
        float_rest = float(obj.rest)
        sumTime3 = sumTime2 - float_rest
        obj.working_time = sumTime3
        # save
        super().save_model(request, obj, form, change)

    #user filter
    def get_queryset(self, request):
        if request.user.is_superuser or request.user.has_perm('attendance.confirm_button_attendance') :
            qs = super().get_queryset(request)
            return qs
        else:
            qs = super().get_queryset(request)
            return qs.filter(user_id = request.user.id)

    #commit
    def commit_button(self, request,queryset):
        for obj in queryset:
            if obj.status != const.WORK_TYPE_SMALL_0:
                messages.add_message(request, messages.ERROR, '未提出记录を選択してください')
                return
            queryset.update(status=const.WORK_TYPE_SMALL_1)
        #mail
        mailUtil.sendmail(const.MAIL_KBN_COMMIT, queryset)
        messages.add_message(request, messages.SUCCESS, '提出済')

    commit_button.short_description = ' 提出'
    commit_button.type = 'success'
    commit_button.confirm = '提出よろしですか？'
    commit_button.icon = 'fas fa-user-check'
    commit_button.allowed_permissions = ('commit_button_attendance',)

    def has_commit_button_attendance_permission(self, request):
        # if request.user.is_superuser or request.user.has_perm('attendance.confirm_button_attendance'):
        if request.user.is_superuser :
            return False
        else:
            opts = self.opts
            codename = get_permission_codename('commit_button', opts)
            return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    #cancel
    def cancel_button(self, request, queryset):
        for obj in queryset:
            if request.user.is_superuser or request.user.has_perm('attendance.confirm_button_attendance'):
                queryset.update(status=const.WORK_TYPE_SMALL_0)
            else:
                if obj.status == const.WORK_TYPE_SMALL_1:
                    queryset.update(status=const.WORK_TYPE_SMALL_0)
                else:
                    messages.add_message(request, messages.ERROR, '提出记录を選択してください')
                    return
                
        #mail
        if request.user.is_superuser or request.user.has_perm('attendance.confirm_button_attendance'):
            mailUtil.sendmail(const.MAIL_KBN_CANCEL, queryset)
        messages.add_message(request, messages.SUCCESS, '取消済')

    cancel_button.short_description = ' 取消'
    cancel_button.type = 'warning'
    cancel_button.icon = 'el-icon-refresh-left'
    cancel_button.confirm = '取消よろしですか？'

    #confirm
    def confirm_button(self, request,queryset):
        tempId = ''
        for obj in queryset:
            if obj.status != const.WORK_TYPE_SMALL_1:
                messages.add_message(request, messages.ERROR, '提出済记录を選択してください')
                return
            queryset.update(status=const.WORK_TYPE_SMALL_2)
        #mail
        mailUtil.sendmail(const.MAIL_KBN_CONFIRM, queryset)
        messages.add_message(request, messages.SUCCESS, '承認済')
    confirm_button.short_description = ' 承認'
    confirm_button.type = 'success'
    confirm_button.confirm = '承認よろしですか？'
    confirm_button.icon = 'fas fa-user-check'
    confirm_button.allowed_permissions = ('confirm_button_attendance',)

    def has_confirm_button_attendance_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('confirm_button', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))
    
    #queryset筛选
    def querysetFilter(self, queryset, expErrList):
        for obj in queryset:
            if obj.status != const.WORK_TYPE_SMALL_2:
                expErrList.append(obj.name + ':' + obj.date.strftime('%Y%m'))
                queryset = queryset.filter(
                    ~(Q(user_id=obj.user_id)
                      &Q(date__startswith=obj.date.strftime('%Y-%m')))
                )
                return self.querysetFilter(queryset=queryset, expErrList=expErrList)
        return queryset

    #excle导出
    def export(self, request, queryset):
        expErrList=[]
        #queryset筛选
        temp_queryset = AttendanceAdmin.querysetFilter(self, queryset, expErrList)

        #mkDir
        folder_name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        if os.path.isdir(const.DIR):
            os.mkdir(os.path.join(const.DIR, folder_name))
        #ErrList write
        errListPath = const.DIR + folder_name + const.FILESTART +'ErrList.txt'
        fp = open(errListPath,'w+')
        for line in expErrList:
            fp.write(line+'\n')
        fp.close()
        
        if len(queryset) != 0:
            #呼出EXCEL制作
            fileUtil.export(temp_queryset, folder_name)
            messages.add_message(request, messages.SUCCESS, 'SUCCESS')

        #ZIp
        temp = const.DIR + folder_name + '.zip'
        temp_zip = zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED)        
        startdir = const.DIR + folder_name
        for dirpath, dirnames, filenames in os.walk(startdir):
            fpath = dirpath.replace(startdir,'') 
            fpath = fpath and fpath + os.sep or ''            
            for filename in filenames:
                temp_zip.write(os.path.join(dirpath, filename),fpath+filename)
        temp_zip.close()
        fread = open(temp_zip.filename,"rb")
        response = HttpResponse(fread, content_type='application/zip')
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(folder_name+".zip")
        fread.close()
        # tempDel
        if os.path.exists(temp):
            os.remove(temp)  
            for root, dirs, files in os.walk(startdir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.removedirs(startdir)
        else:
            print('no such file') 
        return response

    export.short_description = ' 導出'
    export.type = 'primary'
    export.icon = 'el-icon-document-copy'
    export.allowed_permissions = ('export_attendance',)

    def has_export_attendance_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('export', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    class Media:
        js = ('admin/js/admin/attendance.js',)