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
from django.http.response import HttpResponse, Http404
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
from common.custom_filter import DutyDateFieldFilter
from common import fileUtil
from common import mailUtil
from common.const import const

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    # actions
    actions = ['cancel_button', 'commit_button', 'confirm_button', 'export', ]
    # display
    list_display = ('name', 'date', 'duty', 'start_time', 'end_time', 'rest', 'working_time', 'contents', 'status')
    # list
    list_filter = ('status',('date', DateFieldFilter))
    # set search
    search_fields = ('name',)
    # set field
    fieldsets = [(None,{'fields':['date', 'duty', 'start_time', 'end_time', 'rest', 'contents']})]
    # ordering
    ordering = ( 'name', 'date')
    # 一ページ表示の数
    list_per_page = 7

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.status != const.WORK_TYPE_SMALL_0:
                return False
        return super().has_delete_permission(request)

    # user set
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

    # user filter
    def get_queryset(self, request):
        if request.user.is_superuser or request.user.has_perm('attendance.confirm_button_attendance') :
            qs = super().get_queryset(request)
            return qs
        else:
            qs = super().get_queryset(request)
            return qs.filter(user_id = request.user.id)

    # commit
    def commit_button(self, request,queryset):
        for obj in queryset:
            if obj.status != const.WORK_TYPE_SMALL_0:
                messages.add_message(request, messages.ERROR, '未提出记录を選択してください')
                return
            queryset.update(status=const.WORK_TYPE_SMALL_1)
        # mail
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

    # cancel
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

        # mail
        if request.user.is_superuser or request.user.has_perm('attendance.confirm_button_attendance'):
            mailUtil.sendmail(const.MAIL_KBN_CANCEL, queryset)
        messages.add_message(request, messages.SUCCESS, '取消済')

    cancel_button.short_description = ' 取消'
    cancel_button.type = 'warning'
    cancel_button.icon = 'el-icon-refresh-left'
    cancel_button.confirm = '取消よろしですか？'

    # confirm
    def confirm_button(self, request,queryset):
        tempId = ''
        for obj in queryset:
            if obj.status != const.WORK_TYPE_SMALL_1:
                messages.add_message(request, messages.ERROR, '提出済记录を選択してください')
                return
            queryset.update(status=const.WORK_TYPE_SMALL_2)
        # mail
        mailUtil.sendmail(const.MAIL_KBN_CONFIRM, queryset)
        messages.add_message(request, messages.SUCCESS, '承認済')
    # 統計データ抽出
        # 統計リスト定義
        querysetlist = []
        for obj in queryset:
            querysetdir = {}
            # 社員名をキーとして、勤務日付の年月をバリューとして、ディクショナリーに格納する
            querysetdir[obj.name] = obj.date.strftime('%Y-%m')
            # 社員名または勤務日付の年月が違うディクショナリーを統計リストに格納する
            if querysetdir not in querysetlist:
                querysetlist.append(querysetdir)
                continue
        # 統計リストを繰り返し処理、
        index = 0
        while index < len(querysetlist):
            # ディクショナリー毎に社員名、勤務日付の年月の値を統計実行メソッドに渡す
            for keyname in querysetlist[index]:
                valueYM = querysetlist[index][keyname]
                self.attendanceCompute(keyname, valueYM)
            index += 1
    confirm_button.short_description = ' 承認'
    confirm_button.type = 'success'
    confirm_button.confirm = '承認よろしですか？'
    confirm_button.icon = 'fas fa-user-check'
    confirm_button.allowed_permissions = ('confirm_button_attendance',)

    def has_confirm_button_attendance_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('confirm_button', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    # queryset筛选
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

    # excle导出
    def export(self, request, queryset):
        expErrList=[]
        # queryset筛选
        temp_queryset = AttendanceAdmin.querysetFilter(self, queryset, expErrList)

        # mkDir
        folder_name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        if os.path.isdir(const.DIR):
            os.mkdir(os.path.join(const.DIR, folder_name))
        # ErrList write
        errListPath = const.DIR + folder_name + const.FILESTART +'ErrList.txt'
        fp = open(errListPath,'w+')
        for line in expErrList:
            fp.write(line+'\n')
        fp.close()

        if len(queryset) != 0:
            # 呼出EXCEL制作
            fileUtil.export(temp_queryset, folder_name)
            messages.add_message(request, messages.SUCCESS, 'SUCCESS')

        try:
            # ZIp
            temp = const.DIR + folder_name + '.zip'
            temp_zip = zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED)
            startdir = const.DIR + folder_name
            for dirpath, dirnames, filenames in os.walk(startdir):
                fpath = dirpath.replace(startdir, '')
                fpath = fpath and fpath + os.sep or ''
                for filename in filenames:
                    temp_zip.write(os.path.join(dirpath, filename),fpath+filename)
            temp_zip.close()
            fread = open(temp_zip.filename, "rb")
            response = HttpResponse(fread, content_type='application/zip', status=200)
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
        except Exception:
            raise Http404



    export.short_description = ' 導出'
    export.type = 'primary'
    export.icon = 'el-icon-document-copy'
    export.allowed_permissions = ('export_attendance',)


    def has_export_attendance_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('export', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    #勤務統計実行
    def attendanceCompute(self, keyname, valueYM):
        # 承認された勤務年月を取得し、int型に変換
        valueYear = int(valueYM[0:4])
        valueMonth = int(valueYM[5:])
        # 社員名と勤務年月と承認済を条件として,勤怠表からデータ記録をフィルターする　　
        queryset = Attendance.objects.filter(name=keyname, date__year=valueYear, date__month=valueMonth,
                                             status=const.WORK_TYPE_SMALL_2).order_by('name')
        #valueYM型の勤務年月をフォーマットし、勤務統計の統計年月初期値を何年何月1日に設定する
        attendance_YM = datetime.strptime(valueYM, '%Y-%m')
        # 実働時間初期値
        working_time = 0
        # 出勤日数初期値
        attendance_count = 0
        # 欠勤初期値
        absence_count = 0
        # 年休初期値
        annual_leave = 0
        # 休出初期値
        rest_count = 0
        # 遅早退初期値
        late_count = 0
        # マスターコード表から勤務区分の小分類コードを抽出する
        dutymast = CodeMst.objects.filter(cd=const.DUTY_TYPE).values_list('subCd', 'subNm').order_by('subCd')
        for obj in queryset:
            # 実働時間統計
            working_time = working_time + obj.working_time
            # 出勤日数統計
            if obj.duty == dutymast[0][0]:
                attendance_count = attendance_count + 1
            # 欠勤統計
            if obj.duty == dutymast[4][0]:
                absence_count = absence_count + 1
            # 年休統計
            if obj.duty == dutymast[5][0]:
                annual_leave = annual_leave + 1
            # 休出統計
            if obj.duty == dutymast[7][0]:
                rest_count = rest_count + 1
            # 遅早退統計
            if obj.duty == dutymast[1][0] or obj.duty == dutymast[2][0]:
                late_count = late_count + 1
        # 社員ナンバー取得
        empNo = Employee.objects.get(name=keyname).empNo
        # 該当社員の勤務年月のデータ記録をクエリする
        statisticsQuery = DutyStatistics.objects.filter(name=keyname, attendance_YM__year=attendance_YM.year,
                                                              attendance_YM__month=attendance_YM.month)
        # データ記録のクエリ結果有り無しを確認する、無ければデータ登録
        if statisticsQuery.count() == 0:
            DutyStatistics.objects.create(empNo=empNo, name=keyname, attendance_YM=attendance_YM,
                    working_time=working_time, attendance_count=attendance_count, absence_count=absence_count,
                    annual_leave=annual_leave, rest_count=rest_count, late_count=late_count)
        # データ記録のクエリ結果あれば、データ更新
        else:
            statisticsQuery.update(working_time=working_time, attendance_count=attendance_count,
                    absence_count=absence_count, annual_leave=annual_leave, rest_count=rest_count, late_count=late_count)

    class Media:
        js = ('admin/js/admin/attendance.js',)


# 勤務統計モデルadmin
@admin.register(DutyStatistics)
class DutyStatisticsAdmin(admin.ModelAdmin):
    list_display = (
    'empNo', 'name', 'attendance_YM', 'working_time', 'attendance_count', 'absence_count', 'annual_leave', 'rest_count',
    'late_count')
    list_per_page = 7
    search_fields = ('empNo', 'name')
    list_filter = (('attendance_YM', DutyDateFieldFilter),)
    ordering = ('attendance_YM', 'name')
    actions = ['export', ]
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # excle導出
    def export(self, request, queryset):
        # mkDir
        folder_name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        if os.path.isdir(const.DIR):
            os.mkdir(os.path.join(const.DIR, folder_name))
        if len(queryset) != 0:
            # 呼出EXCEL制作
            print(len(queryset))
        # 統計年月開始を取得
        attendance_YM_From = request.GET.get('attendance_YM__gte')[0:7]
        # 統計年月終了を取得
        attendance_YM_To = request.GET.get('attendance_YM__lt')[0:7]
        # 月度単位または年度単位の判断
        if attendance_YM_From == attendance_YM_To:
            # 月度単位の集計表(excel)の導出
            filename = fileUtil.exportExcel(folder_name, attendance_YM_From)
            messages.add_message(request, messages.SUCCESS, 'SUCCESS')
        else:
            # 年度単位の集計表(excel)の導出
            filename = fileUtil.exportYearExcel(folder_name, attendance_YM_From, attendance_YM_To, queryset)
            messages.add_message(request, messages.SUCCESS, 'SUCCESS')
        # ファイルをダウンロード
        fread = open(filename, "rb")
        response = HttpResponse(fread, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename="Report.xlsx"'
        fread.close()
        # サバのフォルダーを削除する
        startdir = const.DIR + folder_name
        if os.path.exists(filename):
            os.remove(filename)
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
    export.allowed_permissions = ('export_dutyStatistics',)


    def has_export_dutyStatistics_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('export', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    # queryset筛选
    def querycount(self, queryset, expErrList):
        for obj in queryset:
            if obj.status != const.WORK_TYPE_SMALL_2:
                expErrList.append(obj.name + ':' + obj.date.strftime('%Y%m'))
                queryset = queryset.filter(
                    ~(Q(user_id=obj.user_id)
                      & Q(date__startswith=obj.date.strftime('%Y-%m')))
                )
                return self.querysetFilter(queryset=queryset, expErrList=expErrList)
        return queryset
