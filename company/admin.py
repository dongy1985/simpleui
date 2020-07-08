from django.contrib import admin
from django.contrib.auth import get_permission_codename
from django.contrib import admin, messages


from common.const import const
from common.custom_filter import DateFieldFilter
from company.models import Detail, Employee, Paysub, Paymain, Apply


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
        obj.applyName = Employee.objects.filter(user_id=request.user.id)
        # # 総金額
        detail_inlines = Detail.objects.filter(apply_id=obj.id)
        obj.totalMoney = 0
        for line in detail_inlines:
            obj.totalMoney = obj.totalMoney + line.trafficExpense
        super().save_model(request, obj, form, change)


@admin.register(Employee)
class Employee(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['name', 'empNo', 'gender', 'birthday', 'email', 'zipCode', 'homeAddr', 'phone', 'user', 'empSts']})]
    list_display = ('name', 'empNo', 'gender', 'birthday', 'email', 'zipCode', 'homeAddr', 'phone', 'empSts')
    search_fields = ('name', 'empNo')
    list_per_page = 20
    raw_id_fields = ('user',)
    list_filter = ('name', 'empNo', 'empSts')

    list_display_links = ('name',)

# 立替金admin
class PaysubInline(admin.TabularInline):
    model = Paysub
    extra = 1  # 默认显示条目的数量
    fieldsets = [(None, {'fields': ['usedate',  'komoku', 'detail_text', 'price']})]

@admin.register(Paymain)
class PaymainAdmin(admin.ModelAdmin):
    inlines = [PaysubInline, ]
    fieldsets = [(None, {'fields': ['applydate', 'bikou_text']})]
    list_display = ('applyer', 'applydate', 'total_money', 'bikou_text', 'status')
    list_filter = ('applyer', 'status', ('applydate', DateFieldFilter))
    list_per_page = 10

    actions = ['tichu_button', 'chengren_button', 'cancel_button']
    def save_model(self, request, obj, form, change):
        obj.user_id = request.user.id
        obj.applyer = Employee.objects.get(user_id=request.user.id).name
        subquery = Paysub.objects.filter(paymain_id=obj.id)
        obj.total_money = 0
        for line in subquery:
            obj.total_money = obj.total_money + line.price
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user_id=request.user.id)

    def tichu_button(self, request, queryset):
        for obj in queryset:
            if obj.status != const.WORK_TYPE_SMALL_0:
                messages.add_message(request, messages.ERROR, '未提出を選んでください！')
                return
        queryset.update(status=const.WORK_TYPE_SMALL_1)

    # 显示的文本，与django admin一致
    tichu_button.short_description = ' 提出'
    # icon，参考element-ui icon与https://fontawesome.com
    tichu_button.icon = 'fas fa-check-circle'
    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    tichu_button.type = 'success'
     # 承認
    def chengren_button(self, request, queryset):
        for obj in queryset:
            if obj.status != const.WORK_TYPE_SMALL_1:
                messages.add_message(request, messages.ERROR, '提出済を選んでください！')
                return
        queryset.update(status=const.WORK_TYPE_SMALL_2)

    # 显示的文本，与django admin一致
    chengren_button.short_description = ' 承認'
    # icon，参考element-ui icon与https://fontawesome.com
    chengren_button.icon = 'fas fa-check-circle'
    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    chengren_button.type = 'success'
    chengren_button.allowed_permissions = ('chengren_button',)

    #承認権限チェック
    def has_chengren_button_permission(self, request):
        if not request.user.is_superuser:
            return False
        opts = self.opts
        codename = get_permission_codename('chengren_button', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))
    #取消
    def cancel_button(self, request, queryset):
        queryset.update(status=const.WORK_TYPE_SMALL_0)
    # 显示的文本，与django admin一致
    cancel_button.short_description = ' 取消'
    # icon，参考element-ui icon与https://fontawesome.com
    cancel_button.icon = 'fas fa-check-circle'
    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    cancel_button.type = 'warning'
