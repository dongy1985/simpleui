from django.contrib import admin
from django.contrib.auth import get_permission_codename
from django.contrib import admin, messages

from submission.models import *
from common.const import const
from common.custom_filter import DateFieldFilter
from common.models import *
from company.models import *
import time
from django.contrib.auth.models import User
from django.contrib import messages
import re
from django.db.models import Q


# 社員admin
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    fieldsets = [(None, {
        'fields': ['name', 'empNo', 'gender', 'birthday', 'email', 'zipCode', 'homeAddr', 'phone', 'retention_code',
                   'retention_limit', 'user', 'empSts']})]

    # 要显示的字段
    def changelist_view(self, request, extra_context=None):
        if request.user.is_superuser:
            self.list_display = ['name', 'empNo', 'email', 'phone']
        else:
            self.list_display = ('name', 'empNo', 'email', 'user_id', )
        return super(EmployeeAdmin, self).changelist_view(request=request, extra_context=None)

    search_fields = ('name', 'empNo')
    list_per_page = const.LIST_PER_PAGE
    raw_id_fields = ('user',)
    list_filter = ('empSts',)
    ordering = ('-empNo',)

    def has_add_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('add', opts)
        query = Employee.objects.filter(user_id=request.user.id)
        if query.count() != 0 and request.user.is_superuser == False:
            return False
        else:
            return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def save_model(self, request, obj, form, change):
        if change:
            # 立替金
            expenRe = ExpenseReturn.objects.filter(user_id=obj.user_id)
            if expenRe.count() != 0:
                expenRe.update(applyer=obj.name)
            # 通勤手当
            applyDuty = ApplyDutyAmount.objects.filter(user_id=obj.user_id)
            if applyDuty.count() != 0:
                applyDuty.update(applyName=obj.name)
            # 資産申請管理
            assetLend = AssetLend.objects.filter(user_id=obj.user_id)
            if assetLend.count() != 0:
                assetLend.update(user_name=obj.name)
            # 勤務管理
            attend = Attendance.objects.filter(user_id=obj.user_id)
            if attend.count() != 0:
                attend.update(name=obj.name)
            # 勤務統計
            dutySta = DutyStatistics.objects.filter(empNo=obj.empNo)
            if dutySta.count() != 0:
                dutySta.update(name=obj.name)
        super().save_model(request, obj, form, change)



# 資産情報
@admin.register(AssetManage)
class AssetManageAdmin(admin.ModelAdmin):
    # 編集必要なレコード
    fieldsets = [(None, {'fields': ['asset', 'type', 'name', 'permission',
                                    'note', ]})]

    # 表示必要なレコード
    list_display = ('asset', 'type', 'name', 'permission',
                    'note',)

    # サーチ必要なレコード
    search_fields = ('asset',)

    list_filter = ('type',)

    # 一ページ表示の数
    list_per_page = const.LIST_PER_PAGE

    actions_on_top = True

    def save_model(self, request, obj, form, change):
        if change:
            query = AssetLend.objects.filter(asset_id=obj.id)
            if query.count() != 0:
                subNm = CodeMst.objects.get(cd=const.ASSET_TYPE, subCd=obj.type).subNm
                query.update(asset_code=obj.asset, type=subNm, name=obj.name)
        super().save_model(request, obj, form, change)


class WorkSiteDetailInline(admin.TabularInline):
    model = WorkSiteDetail
    fieldsets = [(u'', {'fields': ['member', 'from_date', 'to_date']})]
    raw_id_fields = ('member',)
    extra = 0


# 現場情報
@admin.register(WorkSite)
class WorkSiteAdmin(admin.ModelAdmin):
    # メンバーモデル
    inlines = [WorkSiteDetailInline, ]
    # 表示必要なレコード
    list_display = ('project_name', 'site_name', 'from_date', 'to_date', 'site_number', 'manager')
    # ordering
    ordering = ('site_name', 'from_date')
    # 一ページ表示の数
    list_per_page = 7
    # 編集必要なレコード
    fieldsets = [(None, {'fields': ['project_name', 'site_name', 'site_number', 'manager', 'from_date', 'to_date']})]
    # リンク表示必要なレコード
    list_display_links = ('project_name',)
    # サーチ必要なレコード
    search_fields = ('project_name',)
    # 虫めがね
    raw_id_fields = ('manager',)

    # user filter
    def get_queryset(self, request):
        # superuser
        if request.user.is_superuser:
            qs = super().get_queryset(request)
            return qs
        # 現場管理者
        elif request.user.has_perm('attendance.confirm_button_attendance'):
            tempid = Employee.objects.get(user_id=request.user.id).id
            qs = super().get_queryset(request)
            return qs.filter(manager_id=tempid)
        # メンバー
        else:
            messages.add_message(request, messages.ERROR, '現場管理者ではありません')
            tempid = Employee.objects.get(user_id=request.user.id).id
            qs = super().get_queryset(request)
            return qs.filter(manager_id=tempid)
            # elif len(WorkSiteDetail.objects.filter(member_id=tempid).values('manager_id')) != 0:
            #     temp_worksite_id = WorkSiteDetail.objects.filter(member_id=tempid).values('manager_id')
            #     temp_manager_id = WorkSite.objects.filter(id=temp_worksite_id).values('manager_id')
            #     qs = super().get_queryset(request)
            #     return qs.filter(manager=temp_manager_id)
