from django.contrib import admin
from django.contrib.auth import get_permission_codename
from django.contrib import admin, messages

from company.form import EmployeeAdminForm
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
    # 社員情報フォーム導入
    form = EmployeeAdminForm
    # 社員情報フォーム表示のfieldsets制御
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = []
        # スーパーユーザー或いは社員情報を添加する権限を持つユーザーはfieldsets全表示
        if request.user.is_superuser or request.user.has_perm('company.add_employee'):
            self.exclude = []
        # 普通社員のログインユーザーは自分の社員情報を見られる
        elif obj.name == Employee.objects.get(user_id=request.user.id).name:
            self.exclude = []
        # 普通社員のログインユーザーは自分の社員情報以外、他のユーザーの社員情報の名前、社員番号、メールしかを見えない
        else:
            self.exclude.extend(
                ['gender', 'birthday', 'zipCode', 'homeAddr', 'phone', 'retention_code', 'retention_limit', 'user',
                 'empSts'])
        return super(EmployeeAdmin, self).get_form(request, obj, **kwargs)

    fieldsets = [(None, {
        'fields': ['name', 'empNo', 'gender', 'birthday', 'email', 'zipCode', 'homeAddr', 'phone', 'retention_code',
                   'retention_limit', 'user', 'empSts']})]

    # 一覧画面のfieldset表示
    def changelist_view(self, request, extra_context=None):
        # スーパーユーザー或いは社員情報を添加する権限を持つユーザーはfieldsetsの社員情報の名前、社員番号、メールと携帯番号を見える
        if request.user.is_superuser or request.user.has_perm('company.add_employee'):
            self.list_display = ['name', 'empNo', 'email', 'phone']
        # 普通社員は社員情報の名前、社員番号、メールしかを見えない
        else:
            self.list_display = ('name', 'empNo', 'email',)
        return super(EmployeeAdmin, self).changelist_view(request=request, extra_context=None)

    search_fields = ('name', 'empNo')
    list_per_page = const.LIST_PER_PAGE
    raw_id_fields = ('user',)
    list_filter = ('empSts',)
    ordering = ('-empNo',)

    # 社員情報を添加する権限の制御
    def has_add_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('add', opts)
        # 社員情報を添加する権限を持つユーザーとスーパーユーザー以外、添加権限なし
        if request.user.has_perm('company.add_employee') == False and request.user.is_superuser == False:
            return False
        else:
            return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    # 権限別でreadonly制御
    def get_readonly_fields(self, request, obj=None):
        # スーパーユーザー或いは社員情報を添加する権限を持つユーザーは、readonlyのfieldsがない
        if request.user.is_superuser or request.user.has_perm('company.add_employee'):
            self.readonly_fields = []
        # 普通社員は社員情報の名前、社員番号、メールをreadonlyとして設定する
        else:
            self.readonly_fields = ['name', 'empNo', 'email']
        return self.readonly_fields

    # readonly制御
    readonly_fields = ('name', 'empNo', 'email')

    def save_model(self, request, obj, form, change):
        # 社員名が変更される場合、各モジュールの社員名更新
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

    # get_formメソッドと組み合わせとしてfieldsets獲得する
    def get_fieldsets(self, request, obj=None):
        return [(None, {'fields': self.get_fields(request, obj)})]


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
        # 資産情報変更される場合、資産貸出申請の情報を更新する
        if change:
            query = AssetLend.objects.filter(asset_id=obj.id)
            # 該当資産番号を持つ資産貸出申請記録が存在する場合
            if query.count() != 0:
                subNm = CodeMst.objects.get(cd=const.ASSET_TYPE, subCd=obj.type).subNm
                # 資産番号、分類、資産名を更新する
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
    list_per_page = 30
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
        # エス‐ピー
        spUser = User.objects.filter(groups__name='エス‐ピー')
        for obj in spUser:
            if request.user.id == obj.id :
                qs = super().get_queryset(request)
                return qs
        # superuser
        if request.user.is_superuser :
            qs = super().get_queryset(request)
            return qs
        # 現場管理者
        elif request.user.has_perm('submission.confirm_button_attendance'):
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
