from django.contrib import admin
from django.contrib.auth import get_permission_codename
from django.core.checks import messages

from company.models import Apply, Detail
from employee.models import Employe


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
        obj.applyName = Employe.objects.get(user_id=request.user.id).name
        super().save_model(request, obj, form, change)
