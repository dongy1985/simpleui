import time
import calendar
import os
import zipfile
import urllib.parse
import re

from django.contrib import admin, messages
from django.db import transaction
from django.shortcuts import render
from django.contrib.admin import actions
from django.urls import reverse
from django.contrib import admin
from django.contrib.auth import get_user
from django.http.response import HttpResponse, Http404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import get_permission_codename
from django.db.models import Q
from wsgiref.util import FileWrapper
from datetime import date, timedelta
from submission.models import *
from submission.form import *
from common.models import *
from company.models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from common.custom_filter import DateFieldFilter
from common.custom_filter import DutyDateFieldFilter
from common import fileUtil
from common import mailUtil
from common.const import const
from django.db.models import Q

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    form = AttendanceAdminForm
    # actions
    actions = ['commit_button', 'confirm_button', 'cancel_button', 'export', ]
    # display
    list_display = ('name', 'date', 'duty', 'start_time', 'end_time', 'rest', 'working_time', 'contents', 'status')
    # list
    list_filter = ('status',('date', DateFieldFilter))
    # set search
    search_fields = ('name',)
    # set field
    fieldsets = [(None,{'fields':['date', 'duty', 'start_time', 'end_time', 'rest', 'contents']})]
    # ordering
    ordering = ( 'name', '-date')
    # 一ページ表示の数
    list_per_page = const.LIST_PER_PAGE

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.status != const.WORK_TYPE_SMALL_0:
                return False
        return super().has_delete_permission(request)

    # user set
    def save_model(self, request, obj, form, change):
        if obj.status != const.WORK_TYPE_SMALL_0:
            messages.add_message(request, messages.ERROR, '提出済記録が編集できません')
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
        #休憩時間の制御
        sumTime3 = sumTime2 - float_rest
        obj.working_time = sumTime3

        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
                return
        except:
            messages.set_level(request, messages.ERROR)
            temp_errMsg = str(obj.date) + 'の勤務記録は既に存在します，修正してください。'
            messages.error(request, temp_errMsg)
            return

    # user filter
    def get_queryset(self, request):
        if request.user.is_superuser :
            qs = super().get_queryset(request)
            return qs
        elif request.user.has_perm('submission.confirm_button_attendance'):
            qs = super().get_queryset(request)
            temp = None
            employeeId = Employee.objects.get(user_id=request.user.id).id
            workSiteTemp = WorkSite.objects.filter(manager_id = employeeId)
            for obj in workSiteTemp:
                workSiteDetailTemp = WorkSiteDetail.objects.filter(manager_id = obj.id)
                for objD in workSiteDetailTemp:
                    userId = Employee.objects.get(id=objD.member_id).user_id
                    qsTemp = qs.filter(user_id = userId)
                    if temp == None :
                        temp = qsTemp
                    else:
                        querysets = temp | qsTemp
                        temp = querysets
            return temp
        else:
            qs = super().get_queryset(request)
            temp = None
            employeeId = Employee.objects.get(user_id=request.user.id).id
            if len(WorkSite.objects.filter(manager_id = employeeId)) != 0:
                workSiteTemp = WorkSite.objects.filter(manager_id = employeeId)
                for obj in workSiteTemp:
                    workSiteDetailTemp = WorkSiteDetail.objects.filter(manager_id = obj.id)
                    for objD in workSiteDetailTemp:
                        userId = Employee.objects.get(id=objD.member_id).user_id
                        qsTemp = qs.filter(user_id = userId)
                        if temp == None :
                            temp = qsTemp
                        else:
                            querysets = temp | qsTemp
                            temp = querysets
                return temp
            return qs.filter(user_id = request.user.id)

    # commit
    def commit_button(self, request,queryset):
        for obj in queryset:
            if obj.status != const.WORK_TYPE_SMALL_0:
                messages.add_message(request, messages.ERROR, '未提出記録を選択してください')
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
        # if request.user.is_superuser or request.user.has_perm('submission.confirm_button_attendance'):
        if request.user.is_superuser :
            return False
        else:
            opts = self.opts
            codename = get_permission_codename('commit_button', opts)
            return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    # cancel
    def cancel_button(self, request, queryset):
        tempId = ''
        # 統計リスト定義
        querysetslist = []
        for obj in queryset:
            querysetsdir = {}
            # 社員名をキーとして、勤務日付の年月をバリューとして、ディクショナリーに格納する
            querysetsdir[obj.name] = obj.date.strftime('%Y-%m')
            # 社員名または勤務日付の年月が違うディクショナリーを統計リストに格納する
            if querysetsdir not in querysetslist:
                querysetslist.append(querysetsdir)

            if request.user.is_superuser or request.user.has_perm('submission.confirm_button_attendance'):
                queryset.update(status=const.WORK_TYPE_SMALL_0)
            else:
                if obj.status == const.WORK_TYPE_SMALL_1:
                    queryset.update(status=const.WORK_TYPE_SMALL_0)
                else:
                    messages.add_message(request, messages.ERROR, '承認済記録が取消できません')
                    return

        # mail
        if request.user.is_superuser or request.user.has_perm('submission.confirm_button_attendance'):
            mailUtil.sendmail(const.MAIL_KBN_CANCEL, queryset)
        messages.add_message(request, messages.SUCCESS, '取消済')

        # 統計リストを繰り返し処理、
        index = 0
        while index < len(querysetslist):
            # ディクショナリー毎に社員名、勤務日付の年月の値を統計実行メソッドに渡す
            for keyname in querysetslist[index]:
                valueYM = querysetslist[index][keyname]
                self.dutyCompute(keyname, valueYM)
            index += 1

    cancel_button.short_description = ' 取消'
    cancel_button.type = 'warning'
    cancel_button.icon = 'el-icon-refresh-left'
    cancel_button.confirm = '取消よろしですか？'

    # confirm
    def confirm_button(self, request,queryset):
        tempId = ''
        # 統計リスト定義
        querysetlist = []
        for obj in queryset:
            querysetdir = {}
            # 社員名をキーとして、勤務日付の年月をバリューとして、ディクショナリーに格納する
            querysetdir[obj.name] = obj.date.strftime('%Y-%m')
            # 社員名または勤務日付の年月が違うディクショナリーを統計リストに格納する
            if querysetdir not in querysetlist:
                querysetlist.append(querysetdir)

            if obj.status != const.WORK_TYPE_SMALL_1:
                messages.add_message(request, messages.ERROR, '提出済記録を選択してください')
                return
            queryset.update(status=const.WORK_TYPE_SMALL_2)
        # mail
        mailUtil.sendmail(const.MAIL_KBN_CONFIRM, queryset)
        messages.add_message(request, messages.SUCCESS, '承認済')
        # 統計リストを繰り返し処理、
        index = 0
        while index < len(querysetlist):
            # ディクショナリー毎に社員名、勤務日付の年月の値を統計実行メソッドに渡す
            for keyname in querysetlist[index]:
                valueYM = querysetlist[index][keyname]
                self.dutyCompute(keyname, valueYM)
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
            # messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.SUCCESS, '導出しました')

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
            response = HttpResponse(fread, content_type='attendance/zip', status=200)
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

    #勤務承認統計実行
    def dutyCompute(self, keyname, valueYM):
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
        dutyQuery = DutyStatistics.objects.filter(empNo=empNo, name=keyname, attendance_YM__year=attendance_YM.year,
                                                              attendance_YM__month=attendance_YM.month)
        # データ記録のクエリ結果有り無しを確認する、無ければデータ登録
        if dutyQuery.count() == 0:
            DutyStatistics.objects.create(empNo=empNo, name=keyname, attendance_YM=attendance_YM,
                    working_time=working_time, attendance_count=attendance_count, absence_count=absence_count,
                    annual_leave=annual_leave, rest_count=rest_count, late_count=late_count)
        # データ記録のクエリ結果あれば、データ更新
        else:
            dutyQuery.update(working_time=working_time, attendance_count=attendance_count,
                    absence_count=absence_count, annual_leave=annual_leave, rest_count=rest_count, late_count=late_count)
        # データ削除
        if working_time == 0 or working_time == 0.0:
            self.delCompute(keyname, valueYM)

    # 勤務削除データ抽出
    def delete_queryset(self, request, queryset):
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
        index = 0
        while index < len(querysetlist):
            # ディクショナリー毎に社員名、勤務日付の年月の値を統計実行メソッドに渡す
            for keyname in querysetlist[index]:
                valueYM = querysetlist[index][keyname]
                self.delCompute(keyname, valueYM)
            index += 1
        super().delete_queryset(request, queryset)

    # 勤務削除一覧画面query統計実行
    def delCompute(self, keyname, valueYM):
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
        dutyQuery = DutyStatistics.objects.filter(empNo=empNo, name=keyname, attendance_YM__year=attendance_YM.year,
                                                              attendance_YM__month=attendance_YM.month)
        # データ記録のクエリ結果有り無しを確認する、無ければリターンする
        if dutyQuery.count() == 0:
            return
        # 勤務表から出勤日数,欠勤回数,年休回数,休出回数,遅早退回数あるいは実働時間統計が無ければ、そのデータ履歴記録を削除する
        elif (attendance_count == 0 and absence_count == 0 and annual_leave == 0 and rest_count == 0 and late_count == 0) or working_time == 0:
            dutyQuery.delete()
        # データ記録のクエリ結果あれば、データ更新
        else:
            dutyQuery.update(working_time=working_time, attendance_count=attendance_count,
                    absence_count=absence_count, annual_leave=annual_leave, rest_count=rest_count, late_count=late_count)

    # 勤務削除単一モデル統計実行
    def delete_model(self, request, obj):
        keyname = obj.name
        valueYM = obj.date.strftime('%Y-%m')
        self.delCompute(keyname, valueYM)
        super().delete_model(request, obj)

    class Media:
        js = ('admin/js/admin/attendance.js',)



# 勤務統計モデルadmin
@admin.register(DutyStatistics)
class DutyStatisticsAdmin(admin.ModelAdmin):
    list_display = (
    'empNo', 'name', 'attendance_YM', 'working_time', 'attendance_count', 'absence_count', 'annual_leave', 'rest_count',
    'late_count')
    list_per_page = const.LIST_PER_PAGE
    list_filter = (('attendance_YM', DutyDateFieldFilter),)
    ordering = ('-attendance_YM',)
    actions = ['export', ]
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # excle導出
    def export(self, request, queryset):

        # 統計年月の入力をチェック
        if request.GET.__contains__('attendance_YM__gte'):
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
                filename = fileUtil.exportExcel(folder_name, attendance_YM_From)
                messages.add_message(request, messages.SUCCESS, '導出しました')
            else:
                # 年度単位の集計表(excel)の導出
                filename = fileUtil.exportYearExcel(folder_name, attendance_YM_From, attendance_YM_To, queryset)
                messages.add_message(request, messages.SUCCESS, '導出しました')
            # ファイルをダウンロード
            fread = open(filename, "rb")
            outputName = filename[25:46]
            response = HttpResponse(fread, content_type='attendance/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="{fn}"'.format(fn=urllib.parse.quote(outputName))
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
        else:
            messages.add_message(request, messages.ERROR, '統計年月を入力し、「検索」ボタンを押下してください！')
            return

    export.short_description = ' 導出'
    export.type = 'primary'
    # export.confirm = '導出してもよろしいですか？'
    export.icon = 'el-icon-document-copy'
    export.allowed_permissions = ('export_dutystatistics',)


    def has_export_dutystatistics_permission(self, request):
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


class DutydetailInline(admin.TabularInline):
    model = Dutydetail
    fieldsets = [(u'', {'fields': ['trafficMethod', 'trafficFrom', 'trafficTo', 'trafficAmount']})]
    extra = 0


@admin.register(ApplyDutyAmount)
class ApplyDutyAmountAdmin(admin.ModelAdmin):
    inlines = [DutydetailInline, ]
    form = ApplyDutyAmountAdminForm
    # requestをform側にセット
    def get_form(self, request, obj=None, **kwargs):
        ModelForm = super(ApplyDutyAmountAdmin, self).get_form(request, obj, **kwargs)
        class ModelFormMetaClass(ModelForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return ModelForm(*args, **kwargs)
        return ModelFormMetaClass

    list_display = ('applyName', 'applyDate', 'totalAmount', 'trafficStatus')
    list_per_page = 7
    list_filter = ('trafficStatus', ('applyDate', DateFieldFilter))
    fieldsets = [(None, {'fields': ['applyDate']})]
    list_display_links = ('applyName',)
    search_fields = ('applyName',)
    actions = ['commit_button', 'confirm_button', 'cancel_button']

    # 分页显示，一页的数量
    list_per_page = const.LIST_PER_PAGE


    # deleteのチェック
    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.trafficStatus != const.WORK_TYPE_SMALL_0:
                return False
        return super().has_delete_permission(request)

    # 提出ボタン
    def commit_button(self, request, queryset):
        for obj in queryset:
            if obj.trafficStatus != const.WORK_TYPE_SMALL_0:
                messages.add_message(request, messages.ERROR, '未提出記録を選択してください。')
                return
        queryset.update(trafficStatus=const.WORK_TYPE_SMALL_1)
        # mail
        mailUtil.sendmailDutyAmount(const.MAIL_KBN_COMMIT, queryset)
        messages.add_message(request, messages.SUCCESS, '提出済')

    commit_button.short_description = '提出'
    commit_button.type = 'success'
    commit_button.style = 'color:white;'
    commit_button.confirm = '選択された通勤手当レコードを提出よろしいでしょうか？'
    commit_button.icon = 'fas fa-user-check'
    commit_button.allowed_permissions = ('commit_button_duty',)

    # 提出権限チェックは必要です。
    def has_commit_button_duty_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('commit_button', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    # 該当ユーザーのレコードをフィルター
    def get_queryset(self, request):
        if request.user.is_superuser or request.user.has_perm('submission.confirm_button_applydutyamount'):
            qs = super().get_queryset(request)
            return qs
        else:
            qs = super().get_queryset(request)
            return qs.filter(user_id=request.user.id)

    # 承認ボタン
    def confirm_button(self, request, queryset):
        for obj in queryset:
            if obj.trafficStatus != const.WORK_TYPE_SMALL_1:
                messages.add_message(request, messages.ERROR, '提出済の記録を選択してください。')
                return
        queryset.update(trafficStatus=const.WORK_TYPE_SMALL_2)
        # mail
        mailUtil.sendmailDutyAmount(const.MAIL_KBN_CONFIRM, queryset)
        messages.add_message(request, messages.SUCCESS, '承認済')

    confirm_button.short_description = '承認'
    confirm_button.type = 'success'
    confirm_button.style = 'color:white;'
    confirm_button.confirm = '選択された通勤手当レコードを承認よろしいでしょうか？'
    confirm_button.icon = 'fas fa-user-check'
    confirm_button.allowed_permissions = ('confirm_button_duty',)

    def has_confirm_button_duty_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('confirm_button', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    # cancelボタン
    def cancel_button(self, request, queryset):
        for obj in queryset:
            if request.user.is_superuser or request.user.has_perm('submission.confirm_button_applydutyamount'):
                queryset.update(trafficStatus=const.WORK_TYPE_SMALL_0)
            else:
                if obj.trafficStatus == const.WORK_TYPE_SMALL_1:
                    queryset.update(trafficStatus=const.WORK_TYPE_SMALL_0)
                else:
                    messages.add_message(request, messages.ERROR, '提出記録を選択してください')
                    return

        # mail
        if request.user.is_superuser or request.user.has_perm('submission.confirm_button_applydutyamount'):
            mailUtil.sendmailDutyAmount(const.MAIL_KBN_CANCEL, queryset)
        messages.add_message(request, messages.SUCCESS, '取消済')

    cancel_button.short_description = '取消'
    cancel_button.type = 'warning'
    cancel_button.style = 'color:white;'
    cancel_button.confirm = '選択された通勤手当レコードを取消よろしいでしょうか？'
    cancel_button.icon = 'el-icon-upload el-icon--right'
    cancel_button.allowed_permissions = ('cancel_button_duty',)

    def has_cancel_button_duty_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('cancel_button', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    # 保存の場合、該当ユーザーIDをセット
    def save_model(self, request, obj, form, change):
        # ユーザー
        if obj.applyName == '':
            obj.user_id = request.user.id
            obj.applyName = Employee.objects.get(user_id=request.user.id).name
        # 定期券運賃(1ヶ月):総金額
        # 総金額の初期値
        obj.totalAmount = 0
        # form表单form.dataは画面のデータを取得、re.match/re.search匹配字符串
        # ^	匹配字符串的开头
        # $	匹配字符串的末尾例えば： r'(.*) are (.*?) .*'    r'^dutydetail_set.trafficAmount$', obj
        for detail in form.data:
            if re.match('^dutydetail_set.*trafficAmount$', detail):
                if form.data[detail] != "":
                    newStr = detail
                    deleteFlg = newStr.replace("trafficAmount", "DELETE")
                    # deleteFlgは状態”on” and 存在ですか
                    if form.data.__contains__(deleteFlg) and form.data[deleteFlg] == 'on':
                        continue
                    else:
                        # 明細金額DBから取得、”，”が削除する、明細金額にプラス
                        trafficAmount = re.sub("\D", "", form.data[detail])
                        obj.totalAmount = obj.totalAmount + int(trafficAmount)
        totalamount = obj.totalAmount
        #　総金額のスタイルを変更された後、出力　
        obj.totalAmount = "{:,d}".format(totalamount)
        super().save_model(request, obj, form, change)

    # Inlineモデルの値を取得
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=True)
        for obj in instances:
            if obj.trafficAmount.__contains__(','):
                obj.trafficAmount = re.sub("\D", "", obj.trafficAmount)
                amount = int(obj.trafficAmount)
                obj.trafficAmount = "{:,d}".format(amount)
                obj.save()
            else:
                amount = int(obj.trafficAmount)
                obj.price = "{:,d}".format(amount)
                obj.save()


# 立替金admin
class ExpenseReturnDetailInline(admin.TabularInline):
    model = ExpenseReturnDetail
    extra = 0  # デフォルト表示数
    fieldsets = [(None, {'fields': ['usedate', 'detail_type', 'detail_text', 'price']})]


@admin.register(ExpenseReturn)
class ExpenseReturnAdmin(admin.ModelAdmin):
    inlines = [ExpenseReturnDetailInline, ]
    # 立替金フォーム導入
    form = ExpenseReturnAdminForm
    # requestをform側にセット
    def get_form(self, request, obj=None, **kwargs):
        ModelForm = super(ExpenseReturnAdmin, self).get_form(request, obj, **kwargs)
        class ModelFormMetaClass(ModelForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return ModelForm(*args, **kwargs)
        return ModelFormMetaClass

    fieldsets = [(None, {'fields': ['applydate', 'comment']})]
    list_display = ('applyer', 'applydate', 'amount', 'comment', 'status')
    search_fields = ('applyer',)
    list_filter = ('status', ('applydate', DateFieldFilter))
    ordering = ('-applydate',)
    list_per_page = const.LIST_PER_PAGE

    actions = ['commit_button', 'confirm_button', 'cancel_button']

    # モデル保存
    def save_model(self, request, obj, form, change):
        if obj.applyer == '':
            obj.user_id = request.user.id
            obj.applyer = Employee.objects.get(user_id=request.user.id).name
        obj.amount = 0
        for key in form.data:
            if re.match('^expensereturndetail_set-.*-price$', key):
                if form.data[key] != "":
                    delflag = key.replace("price", "DELETE")
                    if delflag in form.data.keys():
                        continue
                    else:
                        price = re.sub("\D", "", form.data[key])
                        obj.amount = obj.amount + int(price)
        amount = obj.amount
        obj.amount = "{:,d}".format(amount)
        super().save_model(request, obj, form, change)

    # Inlineモデルの値を取得
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=True)
        for obj in instances:
            if obj.price.__contains__(','):
                obj.price = re.sub("\D", "", obj.price)
                a = int(obj.price)
                obj.price = "{:,d}".format(a)
                obj.save()
            else:
                a = int(obj.price)
                obj.price = "{:,d}".format(a)
                obj.save()

    # ユーザーマッチ
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.has_perm('submission.confirm_button_expensereturn'):
            return qs
        return qs.filter(user_id=request.user.id)

    # 提出
    def commit_button(self, request, queryset):
        for obj in queryset:
            if obj.status != const.WORK_TYPE_SMALL_0:
                messages.add_message(request, messages.ERROR, '未提出を選んでください！')
                return
        queryset.update(status=const.WORK_TYPE_SMALL_1)
        # mail
        mailUtil.sendmailExpRen(const.MAIL_KBN_COMMIT, queryset)
        messages.add_message(request, messages.SUCCESS, '提出済')

    commit_button.short_description = ' 提出'
    commit_button.icon = 'fas fa-check-circle'
    commit_button.type = 'success'

    # 承認
    def confirm_button(self, request, queryset):
        for obj in queryset:
            if obj.status != const.WORK_TYPE_SMALL_1:
                messages.add_message(request, messages.ERROR, '提出済を選んでください！')
                return
        queryset.update(status=const.WORK_TYPE_SMALL_2)
        # mail
        mailUtil.sendmailExpRen(const.MAIL_KBN_CONFIRM, queryset)
        messages.add_message(request, messages.SUCCESS, '承認済')

    confirm_button.short_description = ' 承認'
    confirm_button.icon = 'fas fa-check-circle'
    confirm_button.type = 'success'
    confirm_button.allowed_permissions = ('confirm_button',)

    # 承認権限チェック
    def has_confirm_button_permission(self, request):
        # if not request.user.is_superuser:
        #     return False
        opts = self.opts
        codename = get_permission_codename('confirm_button', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    # 取消
    def cancel_button(self, request, queryset):
        for obj in queryset:
            if request.user.is_superuser or request.user.has_perm('submission.confirm_button_expensereturn'):
                queryset.update(status=const.WORK_TYPE_SMALL_0)
            else:
                if obj.status == const.WORK_TYPE_SMALL_1:
                    queryset.update(status=const.WORK_TYPE_SMALL_0)
                else:
                    messages.add_message(request, messages.ERROR, '未提出を選択してください')
                    return
        # mail
        if request.user.is_superuser or request.user.has_perm('submission.confirm_button_expensereturn'):
            mailUtil.sendmailExpRen(const.MAIL_KBN_CANCEL, queryset)
        messages.add_message(request, messages.SUCCESS, '取消済')

    cancel_button.short_description = ' 取消'
    cancel_button.icon = 'fas fa-check-circle'
    cancel_button.type = 'warning'

# 資産貸出申請
@admin.register(AssetLend)
class AssetLendAdmin(admin.ModelAdmin):
    # 資産貸出申請フォーム導入
    form = AssetLendAdminForm
    # 一覧画面から資産番号リンククリック、get_formメソッドを使って変更画面へ遷移
    def get_form(self, request, obj=None, **kwargs):
        # 変更画面に最初に該当資産番号の貸出可否状態を貸出可に設定して、該当資産番号の資産情報を更新する
        if kwargs['change'] == True:
            AssetManage.objects.filter(id=obj.asset_id).update(permission=const.LEND_OK)
        return super(AssetLendAdmin, self).get_form(request, obj, **kwargs)

    fieldsets = [(None, {'fields': ['asset', 'lend_time', 'back_time', 'lend_reason',
                                    'note', ]})]

    # 権限別で一覧画面のfieldset表示
    def changelist_view(self, request, extra_context=None):
        user = request.user
        if self.has_manage_permission(request):
            self.list_display = ['asset_code', 'type', 'name', 'user_name', 'apply_time', 'lend_time', 'lend_truetime',
                                 'back_time',
                                 'back_truetime',
                                 'lend_reason', 'note', 'lend_status', ]
        else:
            self.list_display = (
                'asset_code', 'type', 'name', 'apply_time', 'lend_time', 'lend_truetime', 'back_time',
                'back_truetime',
                'lend_reason', 'note', 'lend_status',)
        return super(AssetLendAdmin, self).changelist_view(request=request, extra_context=None)

    # 検索できるフィールド
    search_fields = ('asset_code',)

    raw_id_fields = ('asset',)
    # filter
    list_filter = ('type', 'lend_status',)

    # 一ページの数
    list_per_page = const.LIST_PER_PAGE

    actions_on_top = True

    # ボタン
    actions = ['commit', 'apply_request', 'apply_deny', 'apply_lend', 'apply_back', 'cancel_button']

    # 提出
    def commit(self, request, queryset):
        for obj in queryset:
            # 未提出しかを選ばない
            if obj.lend_status != const.LEND_NOTCOMMIT:
                messages.add_message(request, messages.ERROR, '未提出を選んでください！')
                return
            # 該当資産番号の貸出可否状態を貸出否に設定する
            AssetManage.objects.filter(id=obj.asset).update(permission=const.LEND_NG)
            # 申請済状態を申請済に設定し、申請提出日付をデフォルト値のローカルタイムに設定する
            queryset.update(lend_status=const.LEND_REQUEST, apply_time=time.strftime("%Y-%m-%d", time.localtime()))
        # mail
        mailUtil.sendmailAsset(const.MAIL_KBN_COMMIT, queryset)
        # メッセージ提示
        messages.add_message(request, messages.SUCCESS, '提出済')
    commit.short_description = ' 提出'
    commit.icon = 'fas fa-user-check'
    commit.type = 'success'

    # 承認
    def apply_request(self, request, queryset):
        ids = request.POST.getlist('_selected_action')
        # 申請済状態を申請済から承認済に変更する
        for id in ids:
            AssetLend.objects.filter(id=id, lend_status=const.LEND_REQUEST).update(lend_status=const.LEND_APPLY)
        # 貸出可否状態を貸出否に設定する
        for obj in queryset:
            AssetManage.objects.filter(id=obj.asset).update(permission=const.LEND_NG)
        # mail
        mailUtil.sendmailAsset(const.MAIL_KBN_CONFIRM, queryset)
        messages.add_message(request, messages.SUCCESS, '申請承認完了')

    apply_request.short_description = '承認'
    apply_request.type = 'success'
    apply_request.icon = 'fas fa-user-check'
    apply_request.allowed_permissions = ('manage',)

    # 拒否
    def apply_deny(self, request, queryset):
        ids = request.POST.getlist('_selected_action')
        # 申請済状態を申請済から拒否に変更する
        for id in ids:
            AssetLend.objects.filter(id=id, lend_status=const.LEND_REQUEST).update(lend_status=const.LEND_DENY)
        # 貸出可否状態を貸出可に設定する
        for obj in queryset:
            AssetManage.objects.filter(id=obj.asset).update(permission=const.LEND_OK)
        # mail
        mailUtil.sendmailAsset(const.MAIL_KBN_REJECT, queryset)
        messages.add_message(request, messages.SUCCESS, '申請拒否完了')

    apply_deny.short_description = '拒否'
    apply_deny.type = 'danger'
    apply_deny.icon = 'fas fa-user-check'
    apply_deny.allowed_permissions = ('manage',)

    # 貸出
    def apply_lend(self, request, queryset):
        ids = request.POST.getlist('_selected_action')
        # 申請済状態を承認済から貸出済に変更し、実際貸出日をデフォルト値のローカルタイムに設定する
        for id in ids:
            AssetLend.objects.filter(id=id, lend_status=const.LEND_APPLY).update(
                lend_status=const.LEND_OUT,
                lend_truetime=time.strftime("%Y-%m-%d", time.localtime()),
            )
        # 貸出可否状態を貸出否に設定する
        for obj in queryset:
            AssetManage.objects.filter(id=obj.asset).update(permission=const.LEND_NG)
        # mail
        mailUtil.sendmailAsset(const.MAIL_LEND_OUT, queryset)
        messages.add_message(request, messages.SUCCESS, '貸出完了')

    apply_lend.short_description = '貸出'
    apply_lend.type = 'info'
    apply_lend.icon = 'fas fa-user-check'
    apply_lend.allowed_permissions = ('manage',)

    # 返却
    def apply_back(self, request, queryset):
        ids = request.POST.getlist('_selected_action')
        # 申請済状態を貸出済から返却済に変更し、実際返却日をデフォルト値のローカルタイムに設定する
        for id in ids:
            AssetLend.objects.filter(id=id, lend_status=const.LEND_OUT).update(
                lend_status=const.LEND_BACK,
                back_truetime=time.strftime("%Y-%m-%d", time.localtime()),
            )
        # 貸出可否状態を貸出可に設定する
        for obj in queryset:
            AssetManage.objects.filter(id=obj.asset).update(permission=const.LEND_OK)
        # mail
        mailUtil.sendmailAsset(const.MAIL_LEND_BACK, queryset)
        messages.add_message(request, messages.SUCCESS, '返却完了')

    apply_back.short_description = '返却'
    apply_back.type = 'info'
    apply_back.icon = 'fas fa-user-check'
    apply_back.allowed_permissions = ('manage',)

    # 取消
    def cancel_button(self, request, queryset):
        # querysetの数をカウント
        qc = queryset.count()
        # 繰り返し処理
        for obj in queryset:
            # 該当資産番号の資産貸出記録を検索
            query = AssetLend.objects.filter(asset_id=obj.asset_id)
            # 該当資産番号のステータス
            status = obj.lend_status
            # 返却と拒否以外の該当資産番号の資産貸出記録をカウント
            count = query.filter(~(Q(lend_status=const.LEND_BACK) | Q(lend_status=const.LEND_DENY))).count()
            # スーパーユーザーと管理権限を持つユーザー
            if request.user.is_superuser or request.user.has_perm('submission.manage_assetlend'):
                # 該当記録のステータスは申請済、承認済、貸出済の場合
                if status == const.LEND_REQUEST or status == const.LEND_APPLY or status == const.LEND_OUT:
                    # 返却と拒否以外の該当資産番号の資産貸出記録はない場合
                    if count == 0:
                        # 該当記録のステータスを未提出に変更し、貸出可否状態を貸出否に設定する
                        queryset.update(lend_status=const.LEND_NOTCOMMIT)
                        AssetManage.objects.filter(id=obj.asset).update(permission=const.LEND_NG)
                    # 該当記録のステータスは申請済、承認済、貸出済いずれかの場合
                    if count == 1:
                        # 該当記録のステータスを未提出に変更し、貸出可否状態を貸出否に設定する
                        query.filter(lend_status=obj.lend_status).update(lend_status=const.LEND_NOTCOMMIT)
                        AssetManage.objects.filter(id=obj.asset).update(permission=const.LEND_NG)
                    else:
                        messages.add_message(request, messages.ERROR, obj.asset_code +'が選ばれているため、取消できません!')
                        continue
                # 該当記録のステータスは返却または拒否の場合
                if status == const.LEND_BACK or status == const.LEND_DENY:
                    # 選択される該当記録の資産番号の返却または拒否のquerysetをクエリする
                    new_query = queryset.filter(asset_id=obj.asset_id)
                    # 該当資産番号の返却または拒否の数をカウント
                    new_count = new_query.filter(Q(lend_status=const.LEND_BACK) | Q(lend_status=const.LEND_DENY)).count()
                    # 返却と拒否の資産貸出記録しかない、該当資産番号の返却または拒否の数は一つ、選択される数は複数の場合
                    if count == 0 and new_count == 1 and qc != 1:
                        # 複数の記録のステータスを未提出に変更し、貸出可否状態を貸出否に設定する
                        new_query.filter(lend_status=obj.lend_status).update(lend_status=const.LEND_NOTCOMMIT)
                        AssetManage.objects.filter(id=obj.asset).update(permission=const.LEND_NG)
                    # 返却と拒否の資産貸出記録しかない、該当資産番号の返却または拒否の数は一つ、選択される数は一つの場合
                    elif count == 0 and new_count == 1 and qc == 1:
                        # 当該記録のステータスを未提出に変更し、貸出可否状態を貸出否に設定する
                        queryset.update(lend_status=const.LEND_NOTCOMMIT)
                        AssetManage.objects.filter(id=obj.asset).update(permission=const.LEND_NG)
                    else:
                        messages.add_message(request, messages.ERROR, obj.asset_code + 'が複数の未提出になるため、取消できません!')
                        continue
            # 普通社員の場合、権限は申請済から未提出に変更するのみです
            else:
                # 該当記録は申請済の場合
                if obj.lend_status == const.LEND_REQUEST:
                    # 当該記録のステータスを未提出に変更し、貸出可否状態を貸出否に設定する
                    queryset.update(lend_status=const.LEND_NOTCOMMIT)
                    AssetManage.objects.filter(id=obj.asset).update(permission=const.LEND_NG)
                else:
                    messages.add_message(request, messages.ERROR, '申請済を選択してください')
                    return
        # mail
        if request.user.is_superuser or request.user.has_perm('submission.manage_assetlend'):
            mailUtil.sendmailAsset(const.MAIL_KBN_CANCEL, queryset)
    cancel_button.short_description = ' 取消'
    cancel_button.icon = 'fas fa-check-circle'
    cancel_button.type = 'warning'

    # 管理権限
    def has_manage_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('manage', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    # 保存
    def save_model(self, request, obj, form, change):
        obj.asset_code = AssetManage.objects.get(id=obj.asset_id).asset
        subCd = AssetManage.objects.get(id=obj.asset_id).type
        obj.type = CodeMst.objects.get(cd=const.ASSET_TYPE, subCd=subCd).subNm
        obj.name = AssetManage.objects.get(id=obj.asset_id).name
        # 新規追加
        if not change:
            obj.user_id = request.user.id
            obj.user_name = Employee.objects.get(user_id=request.user.id).name
            AssetManage.objects.filter(id=obj.asset_id).update(permission=const.LEND_NG)
            super().save_model(request, obj, form, change)
        # 変更
        else:
            obj_query = AssetLend.objects.filter(asset_id=obj.asset_id)
            dbcount = obj_query.filter(~(Q(lend_status__exact=const.LEND_BACK) | Q(lend_status__exact=const.LEND_DENY))).count()
            asmanage = AssetManage.objects.filter(id=obj.asset_id)
            # 変更元の資産番号の貸出記録
            asinit = AssetManage.objects.filter(id=form.initial['asset'])
            # 変更後の資産番号と変更元の資産番号は一緒の場合
            if obj.asset_id == form.initial['asset']:
                asmanage.update(permission=const.LEND_NG)
                super().save_model(request, obj, form, change)
            # 該当資産番号を持つ貸出記録がない場合
            elif obj_query.count() == 0:
                # 変更元の資産番号の資産情報の貸出可否状態を貸出可に設定する
                asinit.update(permission=const.LEND_OK)
                # 該当資産番号の資産情報の貸出可否状態を貸出否に設定する
                asmanage.update(permission=const.LEND_NG)
                super().save_model(request, obj, form, change)
            # 該当資産番号を持つ貸出記録が存在する場合、返却と拒否の資産貸出記録がない場合
            elif obj_query.count() != 0 and dbcount == 0:
                # 変更元の資産番号の資産情報の貸出可否状態を貸出可に設定する
                asinit.update(permission=const.LEND_OK)
                # 該当資産番号の資産情報の貸出可否状態を貸出否に設定する
                asmanage.update(permission=const.LEND_NG)
                super().save_model(request, obj, form, change)
            # 該当資産番号を持つ貸出記録がない場合、変更元の資産番号を持つ貸出記録がない場合
            elif obj_query.count() == 0 and AssetLend.objects.filter(asset_id=form.initial['asset']).count() == 0:
                # 変更元の資産番号の資産情報の貸出可否状態を貸出可に設定する
                asinit.update(permission=const.LEND_OK)
                # 該当資産番号の資産情報の貸出可否状態を貸出否に設定する
                asmanage.update(permission=const.LEND_NG)
                super().save_model(request, obj, form, change)
            else:
                messages.set_level(request, messages.ERROR)
                temp_errMsg = str(obj.asset_code) + '既に選ばれていました、別の資産番号を選んでください。'
                messages.error(request, temp_errMsg)
                return

    # 名前マッチ
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif self.has_manage_permission(request):
            return qs
        return qs.filter(user_id=request.user.id)

    # 拒否以外の記録を削除する場合、貸出可否状態を貸出可に設定する
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.lend_status != const.LEND_DENY:
                AssetManage.objects.filter(id=obj.asset_id).update(permission=const.LEND_OK)
        super().delete_queryset(request, queryset)

    # 未提出の記録を削除する場合、貸出可否状態を貸出可に設定する
    def delete_model(self, request, obj):
        AssetManage.objects.filter(id=obj.asset_id).update(permission=const.LEND_OK)
        super().delete_model(request, obj)