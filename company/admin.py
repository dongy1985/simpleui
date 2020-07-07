from django.contrib import admin
from django.contrib.auth import get_permission_codename
from django.core.checks import messages

from company.models import Apply, Detail, Employee, Expenditure, Statement, Manage, Lend
from employee.models import Employe
import time
from django.contrib.auth.models import User
from django.contrib import messages
from common.const import const

class DetailInline(admin.TabularInline):
    model = Detail
    fieldsets = [(u'', {'fields': ['trafficMethod', 'trafficSectionStart', 'trafficSectionEnd', 'trafficExpense']})]
    extra = 1


@admin.register(Apply)
class ApplyAdmin(admin.ModelAdmin):
    inlines = [DetailInline, ]

    list_display = ('applyName', 'applyDate', 'totalMoney')
    list_per_page = 7
    list_filter = ('applyName',)
    fieldsets = [(None, {'fields': ['applyDate']})]
    list_display_links = ('applyName',)
    actions = ['commit_button', 'confirm_button', 'cancel_button']

    # 提出ボタン
    def commit_button(self, request, queryset):
        for obj in queryset:
            if obj.traffic_status != '0':
                messages.add_message(request, messages.ERROR, '未提出記録を選択してください。')
                return
        queryset.update(traffic_status='1')

    commit_button.short_description = '提出'
    commit_button.type = 'success'
    commit_button.style = 'color:white;'
    commit_button.confirm = '選択された勤務管理レコードを提出よろしいでしょうか？'
    commit_button.icon = 'fas fa-user-check'
    commit_button.allowed_permissions = ('commit_button_duty',)

    # 提出権限チェックは必要です。
    def has_commit_button_duty_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('commit_button', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    # 該当ユーザーのレコードをフィルター
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user_id=request.user.id)

    # 承認ボタン
    def confirm_button(self, request, queryset):
        for obj in queryset:
            if obj.traffic_status != '1':
                messages.add_message(request, messages.ERROR, '提出済の記録を選択してください。')
                return
        queryset.update(traffic_status='2')

    confirm_button.short_description = '承認'
    confirm_button.type = 'success'
    confirm_button.style = 'color:white;'
    confirm_button.confirm = '選択された勤務管理レコードを承認よろしいでしょうか？'
    confirm_button.icon = 'fas fa-user-check'
    confirm_button.allowed_permissions = ('confirm_button_duty',)

    def has_confirm_button_duty_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('confirm_button', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    # cancelボタン
    def cancel_button(self, request, queryset):
        for obj in queryset:
            if obj.traffic_status == '2':
                queryset.update(traffic_status='0')
            else:
                if obj.traffic_status == '1':
                    queryset.update(traffic_status='0')

    cancel_button.short_description = 'キャンセル'
    cancel_button.type = 'warning'
    cancel_button.style = 'color:white;'
    cancel_button.confirm = '選択された勤務管理レコードを取消よろしいでしょうか？'
    cancel_button.icon = 'el-icon-upload el-icon--right'
    cancel_button.allowed_permissions = ('cancel_button_duty',)

    def has_cancel_button_duty_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('cancel_button', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    # 保存の場合、該当ユーザーIDをセット
    def save_model(self, request, obj, form, change):
        obj.user_id = request.user.id
        obj.applyName = Employee.objects.get(user_id=request.user.id).name
        # # 総金額
        detail_inlines = Detail.objects.filter(apply_id=obj.id)
        obj.totalMoney = 0
        for line in detail_inlines:
            obj.totalMoney = obj.totalMoney + line.trafficExpense
        super().save_model(request, obj, form, change)

@admin.register(Employee)
class Employee(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['name', 'empNo', ' gender', 'birthday', 'email', 'zipCode', 'homeAddr', 'phone', 'user', 'empSts']})]
    list_display = ('name', 'empNo', ' gender', 'birthday', 'email', 'zipCode', 'homeAddr', 'phone', 'empSts')
    search_fields = ('name', 'empNo')
    list_per_page = 20
    raw_id_fields = ('user',)
    list_filter = ('name', 'empNo', 'empSts')

    list_display_links = ('name',)


# 資産合計
@admin.register(Expenditure)
class ExpenditureAdmin(admin.ModelAdmin):
    inlines = [DetailInline2, ]

    # 編集必要なレコード
    fieldsets = [(None, {'fields': ['name', 'buy_date', 'unit_price', 'number',
                                    'note', ]})]

    # 表示必要なレコード
    list_display = ('name', 'buy_date', 'unit_price', 'number', 'total_price',
                    'note',)

    # サーチ必要なレコード
    search_fields = ('name',)

    # 一ページ表示の数
    list_per_page = const.PAGES

    actions_on_top = True

    # 金額計算
    def save_model(self, request, obj, form, change):
        obj.total_price = obj.unit_price * obj.number
        super().save_model(request, obj, form, change, )


# 資産状態
@admin.register(Manage)
class ManageAdmin(admin.ModelAdmin):
    # 編集必要なレコード
    fieldsets = [(None, {'fields': ['name_code', 'kind', 'name', 'permission',
                                    'note', ]})]

    # 表示必要なレコード
    list_display = ('name_code', 'kind', 'name', 'permission',
                    'note',)

    # サーチ必要なレコード
    search_fields = ('name_code',)

    list_filter = ('kind',)

    # 一ページ表示の数
    list_per_page = const.PAGES

    actions_on_top = True


# 資産借出申請
@admin.register(Lend)
class LendAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['name_code', 'lend_time', 'back_time', 'lend_reason',
                                    'note', ]})]

    # 要显示的字段
    list_display = (
        'real_code', 'kind', 'name', 'user_name', 'apply_time', 'lend_time', 'lend_truetime', 'back_time',
        'back_truetime',
        'lend_reason', 'note', 'lend_status',)

    # 需要搜索的字段
    # search_fields = ('name_code',)

    raw_id_fields = ('name_code',)
    # filter
    list_filter = ('kind', 'lend_status',)

    # 分页显示，一页的数量
    list_per_page = const.PAGES

    actions_on_top = True

    # ボタン
    actions = ['apply_request', 'apply_deny', 'apply_lend', 'apply_back', ]

    # 承認
    def apply_request(self, request, queryset):
        ids = request.POST.getlist('_selected_action')
        for id in ids:
            Lend.objects.filter(id=id, lend_status=const.LEND_REQUEST).update(
                lend_status=const.LEND_APPLY,
            )
        for obj in queryset:
            Manage.objects.filter(id=obj.name_code_id).update(
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
            Lend.objects.filter(id=id, lend_status=const.LEND_REQUEST).update(
                lend_status=const.LEND_DENY,
            )
        messages.add_message(request, messages.SUCCESS, '申請拒否完了')

    apply_deny.short_description = '拒否'

    apply_deny.type = 'danger'

    apply_deny.icon = 'fas fa-user-check'

    apply_deny.allowed_permissions = ('apply',)

    # 借出
    def apply_lend(self, request, queryset):
        ids = request.POST.getlist('_selected_action')
        for id in ids:
            Lend.objects.filter(id=id, lend_status=const.LEND_APPLY).update(
                lend_status=const.LEND_OUT,
                lend_truetime=time.strftime("%Y-%m-%d", time.localtime()),
            )
        messages.add_message(request, messages.SUCCESS, '借出完了')

    apply_lend.short_description = '借出'

    apply_lend.type = 'info'

    apply_lend.icon = 'fas fa-user-check'

    apply_lend.allowed_permissions = ('apply',)

    # 返済
    def apply_back(self, request, queryset):
        ids = request.POST.getlist('_selected_action')
        for id in ids:
            Lend.objects.filter(id=id, lend_status=const.LEND_OUT).update(
                lend_status=const.LEND_BACK,
                back_truetime=time.strftime("%Y-%m-%d", time.localtime()),
            )
        for obj in queryset:
            Manage.objects.filter(id=obj.name_code_id).update(
                permission=const.LEND_OK,
            )
        messages.add_message(request, messages.SUCCESS, '返済完了')

    apply_back.short_description = '返済'

    apply_back.type = 'info'

    apply_back.icon = 'fas fa-user-check'

    apply_back.allowed_permissions = ('apply',)

    # 権限
    def has_apply_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('apply', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    # 保存TODO
    def save_model(self, request, obj, form, change):
        obj.worker_number = request.user.id
        obj.user_name = User.objects.get(id=request.user.id).username
        obj.real_code = Manage.objects.get(id=obj.name_code).name_code
        obj.kind = Manage.objects.get(id=obj.name_code).kind
        obj.name = Manage.objects.get(id=obj.name_code).name
        super().save_model(request, obj, form, change, )

    # 名前マッチ
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(worker_number=request.user.id)

  