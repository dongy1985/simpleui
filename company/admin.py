from django.contrib import admin
from django.contrib.auth import get_permission_codename
from django.contrib import admin, messages
from common.const import const
from common.custom_filter import DateFieldFilter
from company.models import Dutydetail, ExpenseReturn, ExpenseReturnDetail, ApplyDutyAmount, Employee, AssetManage, \
    AssetLend, WorkSiteDetail, WorkSite
import time
from django.contrib.auth.models import User
from django.contrib import messages
import re
from django.db.models import Q


class DutydetailInline(admin.TabularInline):
    model = Dutydetail
    fieldsets = [(u'', {'fields': ['trafficMethod', 'trafficFrom', 'trafficTo', 'trafficAmount']})]
    extra = 1


@admin.register(ApplyDutyAmount)
class ApplyDutyAmountAdmin(admin.ModelAdmin):
    inlines = [DutydetailInline, ]

    list_display = ('applyName', 'applyDate', 'totalAmount', 'trafficStatus')
    list_per_page = 7
    list_filter = ('trafficStatus', ('applyDate', DateFieldFilter))
    fieldsets = [(None, {'fields': ['applyDate']})]
    list_display_links = ('applyName',)
    search_fields = ('name',)
    actions = ['commit_button', 'confirm_button', 'cancel_button']

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
        if request.user.is_superuser or request.user.has_perm('company.confirm_button_applydutyamount'):
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
            if request.user.is_superuser or request.user.has_perm('company.confirm_button_applydutyamount'):
                queryset.update(trafficStatus=const.WORK_TYPE_SMALL_0)
            else:
                if obj.trafficStatus == const.WORK_TYPE_SMALL_1:
                    queryset.update(trafficStatus=const.WORK_TYPE_SMALL_0)
                else:
                    messages.add_message(request, messages.ERROR, '提出记录を選択してください')
                    return

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
        #　総金額の初期値
        obj.totalAmount = 0
        # form表单form.dataは画面のデータを取得、re.match/re.search匹配字符串
        # ^	匹配字符串的开头
        # $	匹配字符串的末尾例えば： r'(.*) are (.*?) .*'    r'^dutydetail_set.trafficAmount$', obj
        for detail in form.data:
            if re.match('^dutydetail_set.*trafficAmount$', detail):
               if form.data[detail] != "":
                  newStr = detail
                  deleteFlg = newStr.replace("trafficAmount","DELETE")
                  # deleteFlgは状態”on” and 存在ですか
                  if form.data.__contains__(deleteFlg) and form.data[deleteFlg] == 'on':
                     continue
                  else:
                     obj.totalAmount = obj.totalAmount + int(form.data[detail])
        super().save_model(request, obj, form, change)



# 社員admin
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    fieldsets = [(None, {
        'fields': ['name', 'empNo', 'gender', 'birthday', 'email', 'zipCode', 'homeAddr', 'phone', 'retention_code',
                   'retention_limit', 'user', 'empSts']})]
    list_display = ('name', 'empNo', 'email', 'phone')
    search_fields = ('name', 'empNo')
    list_per_page = 20
    raw_id_fields = ('user',)
    list_filter = ('empSts',)

    list_display_links = ('name',)


# 立替金admin
class ExpenseReturnDetailInline(admin.TabularInline):
    model = ExpenseReturnDetail
    extra = 1  # デフォルト表示数
    fieldsets = [(None, {'fields': ['usedate', 'detail_type', 'detail_text', 'price']})]


@admin.register(ExpenseReturn)
class ExpenseReturnAdmin(admin.ModelAdmin):
    inlines = [ExpenseReturnDetailInline, ]
    fieldsets = [(None, {'fields': ['applydate', 'comment']})]
    list_display = ('applyer', 'applydate', 'amount', 'comment', 'status')
    list_filter = ('applyer', 'status', ('applydate', DateFieldFilter))
    list_per_page = 10

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
                        obj.amount = obj.amount + int(form.data[key])
        super().save_model(request, obj, form, change)


    # ユーザーマッチ
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user_id=request.user.id)

    # 提出
    def commit_button(self, request, queryset):
        for obj in queryset:
            if obj.status != const.WORK_TYPE_SMALL_0:
                messages.add_message(request, messages.ERROR, '未提出を選んでください！')
                return
        queryset.update(status=const.WORK_TYPE_SMALL_1)

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

    confirm_button.short_description = ' 承認'
    confirm_button.icon = 'fas fa-check-circle'
    confirm_button.type = 'success'
    confirm_button.allowed_permissions = ('confirm_button',)

    # 承認権限チェック
    def has_confirm_button_permission(self, request):
        if not request.user.is_superuser:
            return False
        opts = self.opts
        codename = get_permission_codename('confirm_button', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    # 取消
    def cancel_button(self, request, queryset):
        queryset.update(status=const.WORK_TYPE_SMALL_0)

    cancel_button.short_description = ' 取消'
    cancel_button.icon = 'fas fa-check-circle'
    cancel_button.type = 'warning'


# 資産管理
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
    list_per_page = const.PAGES

    actions_on_top = True


# 資産貸出申請
@admin.register(AssetLend)
class AssetLendAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['asset', 'lend_time', 'back_time', 'lend_reason',
                                    'note', ]})]

    # 要显示的字段
    def changelist_view(self, request, extra_context=None):
        user = request.user

        if self.has_apply_permission(request):
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

    # 需要搜索的字段
    # search_fields = ('asset',)

    raw_id_fields = ('asset',)
    # filter
    list_filter = ('type', 'lend_status',)

    # 分页显示，一页的数量
    list_per_page = const.PAGES

    actions_on_top = True

    # ボタン
    actions = ['apply_request', 'apply_deny', 'apply_lend', 'apply_back', ]

    # 承認
    def apply_request(self, request, queryset):
        ids = request.POST.getlist('_selected_action')
        for id in ids:
            AssetLend.objects.filter(id=id, lend_status=const.LEND_REQUEST).update(
                lend_status=const.LEND_APPLY,
            )
        for obj in queryset:
            AssetManage.objects.filter(id=obj.asset).update(
                permission=const.LEND_NG,
            )
        messages.add_message(request, messages.SUCCESS, '申請承認完了')

    apply_request.short_description = '承認'

    apply_request.type = 'success'

    apply_request.icon = 'fas fa-user-check'

    apply_request.allowed_permissions = ('apply',)

    # 拒否
    def apply_deny(self, request, queryset):
        ids = request.POST.getlist('_selected_action')
        for id in ids:
            AssetLend.objects.filter(id=id, lend_status=const.LEND_REQUEST).update(
                lend_status=const.LEND_DENY,
            )
        messages.add_message(request, messages.SUCCESS, '申請拒否完了')

    apply_deny.short_description = '拒否'

    apply_deny.type = 'danger'

    apply_deny.icon = 'fas fa-user-check'

    apply_deny.allowed_permissions = ('apply',)

    # 貸出
    def apply_lend(self, request, queryset):
        ids = request.POST.getlist('_selected_action')
        for id in ids:
            AssetLend.objects.filter(id=id, lend_status=const.LEND_APPLY).update(
                lend_status=const.LEND_OUT,
                lend_truetime=time.strftime("%Y-%m-%d", time.localtime()),
            )
        messages.add_message(request, messages.SUCCESS, '貸出完了')

    apply_lend.short_description = '貸出'

    apply_lend.type = 'info'

    apply_lend.icon = 'fas fa-user-check'

    apply_lend.allowed_permissions = ('apply',)

    # 返却
    def apply_back(self, request, queryset):
        ids = request.POST.getlist('_selected_action')
        for id in ids:
            AssetLend.objects.filter(id=id, lend_status=const.LEND_OUT).update(
                lend_status=const.LEND_BACK,
                back_truetime=time.strftime("%Y-%m-%d", time.localtime()),
            )
        for obj in queryset:
            AssetManage.objects.filter(id=obj.asset).update(
                permission=const.LEND_OK,
            )
        messages.add_message(request, messages.SUCCESS, '返却完了')

    apply_back.short_description = '返却'

    apply_back.type = 'info'

    apply_back.icon = 'fas fa-user-check'

    apply_back.allowed_permissions = ('apply',)

    # 権限
    def has_apply_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('apply', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    # 保存
    def save_model(self, request, obj, form, change):
        if change == False:
            obj.user_id = request.user.id
            obj.user_name = User.objects.get(id=request.user.id).username
        obj.asset_code = AssetManage.objects.get(id=obj.asset).asset
        obj.type = AssetManage.objects.get(id=obj.asset).type
        obj.name = AssetManage.objects.get(id=obj.asset).name
        super().save_model(request, obj, form, change, )

    # 名前マッチ
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user_id=request.user.id)

class WorkSiteDetailInline(admin.TabularInline):
    model = WorkSiteDetail
    fieldsets = [(u'', {'fields': ['member']})]
    raw_id_fields = ('member',)
    extra = 1

# 現場管理
@admin.register(WorkSite)
class WorkSiteAdmin(admin.ModelAdmin):
    # メンバーモデル
    inlines = [WorkSiteDetailInline, ]
    # 表示必要なレコード
    list_display = ('project_name', 'site_name', 'site_number', 'manager')
    # 一ページ表示の数
    list_per_page = 7
    # 編集必要なレコード
    fieldsets = [(None, {'fields': ['project_name', 'site_name', 'site_number', 'manager']})]
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