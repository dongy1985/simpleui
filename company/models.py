from datetime import datetime
from django.contrib.auth.models import User
from django.core import validators
from django.db import models
from django.utils import timezone
from common.const import const
from common.models import CodeMst
import time


# Create your models here
# 通勤手当モデル
class ApplyDutyAmount(models.Model):
    # ユーザー
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='apply_user')
    # 通勤手当申請者名前
    applyName = models.CharField(verbose_name='申請者', max_length=30)
    # 通勤手当申請日付
    applyDate = models.DateField(verbose_name='申請日', default=timezone.now)
    # 定期券運賃(1ヶ月):総金額
    totalAmount = models.CharField(verbose_name='定期券運賃(1ヶ月)', max_length=125, default='')
    # 状態
    stsList = CodeMst.objects.filter(cd=const.WORK_TYPE).values_list('subCd', 'subNm').order_by('subCd')
    trafficStatus = models.CharField(choices=stsList, verbose_name='状態', max_length=3, default=const.WORK_TYPE_SMALL_0)

    class Meta:
        verbose_name = "通勤手当"
        verbose_name_plural = "通勤手当"
        permissions = (
            ("commit_button_applydutyamount", "Can 提出"),
            ("confirm_button_applydutyamount", "Can 承認"),
            ("cancel_button_applydutyamount", "Can 取消"),
        )

    def __str__(self):
        return self.applyName


# 通勤手当明細モデル
class Dutydetail(models.Model):
    # ForeignKey
    apply = models.ForeignKey(ApplyDutyAmount, on_delete=models.CASCADE, verbose_name='申請者', max_length=128, default='')
    # 交通機関
    trafficMethod = models.CharField(verbose_name='交通機関', max_length=125, default='')
    # 開始区間
    trafficFrom = models.CharField(verbose_name='開始区間', max_length=12, default='')
    # 終了区間
    trafficTo = models.CharField(verbose_name='終了区間', max_length=12, default='')
    # 定期券運賃(1ヶ月):交通金額明細
    trafficAmount = models.CharField(verbose_name='金額', max_length=10, default='', validators=[validators.RegexValidator("^\d{1,3}(,\d{3})*$", message='正しい金額を入力してください！')])

    class Meta:
        verbose_name = "通勤手当明細"
        verbose_name_plural = "通勤手当明細"

    def __str__(self):
        return self.trafficMethod


# 社員モデル
class Employee(models.Model):
    # 社員名前
    name = models.CharField(max_length=30, verbose_name='社員名前', null=False, blank=False, db_index=True)
    # 社員番号
    empNo = models.CharField(unique=True, verbose_name='社員番号', max_length=3, null=False, blank=False)
    # 性别
    gender_choices = CodeMst.objects.filter(cd=const.GENDER_CD).values_list('subCd', 'subNm').order_by('subCd')
    gender = models.CharField(max_length=3, choices=gender_choices, verbose_name='性别', default=const.GENDER_DEF)
    # 生年月日
    birthday = models.DateField(verbose_name='生年月日')
    # メールアドレス
    email = models.EmailField(max_length=120, verbose_name='メールアドレス')
    # 自宅郵便番号
    zipCode = models.CharField(verbose_name='自宅郵便番号', max_length=7, null=False, blank=False,
                               help_text='自宅郵便番号を7桁入力してください.例：1010031')
    # 住所
    homeAddr = models.TextField(max_length=360, verbose_name='住所')
    # 電話番号
    phone = models.CharField(max_length=11, verbose_name='電話番号')
    # 在留カード番号
    retention_code = models.CharField(max_length=12, verbose_name='在留カード', null=True, blank=True)
    # 在留カード期限
    retention_limit = models.DateField(verbose_name='在留期限', null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=False, null=True, verbose_name='ログインユーザー',
                             db_index=True)
    # 社員状態
    status_choices = CodeMst.objects.filter(cd=const.EMPLOYEE_CD).values_list('subCd', 'subNm').order_by('subCd')
    empSts = models.CharField(max_length=3, choices=status_choices, verbose_name='社員状態', default=const.EMPLOYEE_DEF)

    # 登録日付
    create_time = models.DateTimeField(verbose_name='登録日付', auto_now=True)
    # 更新日付
    update_time = models.DateTimeField(verbose_name='更新日付', auto_now=True)

    class Meta:
        verbose_name = "社員"
        verbose_name_plural = "社員情報"

    def __str__(self):
        return self.name


# 資産管理
class AssetManage(models.Model):
    # 資産番号
    asset = models.CharField(unique=True, max_length=const.NAME_LENGTH, verbose_name='資産番号')

    # 分類
    type = models.CharField(max_length=const.NAME_LENGTH, verbose_name='分類')

    # 名称
    name = models.CharField(max_length=const.NAME_LENGTH, verbose_name='名称')

    # 貸出可否
    permission = models.BooleanField(verbose_name='貸出可否', default=False)

    # 備考
    note = models.TextField(max_length=const.TEXT_LENGTH, verbose_name='備考', null=True, blank=True)

    class Meta:
        verbose_name = "資産管理"
        verbose_name_plural = "資産管理"

    def __int__(self):
        return self.id

    def __str__(self):
        return self.asset


# 資産借出
class AssetLend(models.Model):
    # 資産番号
    asset = models.ForeignKey(AssetManage, on_delete=models.SET_NULL, blank=False, null=True, verbose_name='資産番号',
                              db_index=True, limit_choices_to={'permission': '1'})

    # 表示番号
    asset_code = models.CharField(max_length=const.NAME_LENGTH, verbose_name='資産番号')

    # 分類
    type = models.CharField(max_length=const.NAME_LENGTH, verbose_name='分類')

    # 名称
    name = models.CharField(max_length=const.NAME_LENGTH, verbose_name='名称')

    # user id
    user_id = models.CharField(max_length=const.TEXT_LENGTH)

    # 貸出対象
    user_name = models.CharField(max_length=const.NAME_LENGTH, verbose_name='貸出対象')

    # 申請提出日付
    apply_time = models.DateField(verbose_name='申請提出日', default=time.strftime("%Y-%m-%d"))

    # 貸出予定日
    lend_time = models.DateField(verbose_name='貸出予定日', default=time.strftime("%Y-%m-%d"))

    # 実際貸出日
    lend_truetime = models.DateField(verbose_name='貸出日', null=True, blank=True)

    # 返却予定日
    back_time = models.DateField(verbose_name='返却予定日', default=time.strftime("%Y-%m-%d"))

    # 実際返却日
    back_truetime = models.DateField(verbose_name='返却日', null=True, blank=True)

    # 用途
    lend_reason = models.CharField(max_length=const.TEXT_LENGTH, verbose_name='用途')

    # 備考
    note = models.TextField(max_length=const.TEXT_LENGTH, verbose_name='備考', null=True, blank=True)

    lend_status_choices = CodeMst.objects.filter(cd=const.BIG_STATUS).values_list('subCd',
                                                                                  'subNm').order_by(
        'subCd')

    # 申請貸出状態
    lend_status = models.CharField(max_length=const.NAME_LENGTH, choices=lend_status_choices, verbose_name='申請状態'
                                   , default=const.LEND_STATUS)

    class Meta:
        verbose_name = "資産貸出申請"
        verbose_name_plural = "資産貸出申請"
        permissions = (
            ("apply_assetlend", "Can apply 資産貸出申請"),
        )

    def __int__(self):
        return self.asset


# 立替金モデル
class ExpenseReturn(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='list_cur_applyer', )
    # 申請者名
    applyer = models.CharField(max_length=30, verbose_name='申請者名')
    # 提出日付
    applydate = models.DateField(verbose_name='提出日付')
    # 総金額
    amount = models.CharField(max_length=30, verbose_name='総金額', default='')
    # 申请状態
    status_choices = CodeMst.objects.filter(cd=const.WORK_TYPE).values_list('subCd', 'subNm').order_by('subCd')
    status = models.CharField(max_length=3, choices=status_choices, verbose_name='申请状態',
                              default=const.WORK_TYPE_SMALL_0)
    # 備考
    comment = models.CharField(max_length=180, verbose_name='備考')

    class Meta:
        verbose_name = "立替金"
        verbose_name_plural = "立替金"
        permissions = (
            ("commit_button_expensereturn", "Can 提出"),
            ("confirm_button_expensereturn", "Can 承認")
        )

    def __str__(self):
        return self.applyer


class ExpenseReturnDetail(models.Model):
    expenseReturn = models.ForeignKey(ExpenseReturn, on_delete=models.CASCADE, )
    # 費用項目
    detail_type = models.CharField(max_length=30, verbose_name='費用項目')
    # 用途
    detail_text = models.CharField(max_length=180, verbose_name='用途')
    # 単一金額
    price = models.CharField(verbose_name='単一金額', max_length=10, default='', validators=[validators.RegexValidator("^\d{1,3}(,\d{3})*$", message='正しい金額を入力してください！')])
    # 使用日付
    usedate = models.DateField(verbose_name='使用日付')

    class Meta:
        verbose_name = "项目明细"
        verbose_name_plural = "项目明细"

    def __str__(self):
        return self.detail_type


# 現場管理モデル
class WorkSite(models.Model):
    # 案件名称
    project_name = models.CharField(max_length=30, verbose_name='案件名称')
    # 現場名称
    site_name = models.CharField(max_length=30, verbose_name='現場名称')
    # 発注番号
    site_number = models.CharField(max_length=16, verbose_name='発注番号')
    # 案件開始日付
    from_date = models.DateField(verbose_name='案件開始日付', default=timezone.now)
    # 案件終了日付
    to_date = models.DateField(verbose_name='案件終了日付', default=datetime.strptime(str('2999-12-31'), '%Y-%m-%d'))

    # 現場責任者
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=False, null=True, verbose_name='現場責任者',
                                db_index=True)

    class Meta:
        verbose_name = "現場管理"
        verbose_name_plural = "現場管理"


# メンバーモデル
class WorkSiteDetail(models.Model):
    # ForeignKey
    manager = models.ForeignKey(WorkSite, on_delete=models.CASCADE, verbose_name='申請者', max_length=128, default='')
    # メンバー
    member = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=False, null=True, verbose_name='メンバー',
                               db_index=True)
    # 備考
    comment = models.CharField(max_length=180, verbose_name='備考', default=const.DEF_COMMENT)
    # 案件開始日付
    from_date = models.DateField(verbose_name='案件開始日付')
    # 案件終了日付
    to_date = models.DateField(verbose_name='案件終了日付', default=datetime.strptime(str('2999-12-31'), '%Y-%m-%d'))

    class Meta:
        verbose_name = "メンバー"
        verbose_name_plural = "メンバー"

    def __int__(self):
        return self.id

    def __str__(self):
        return self.comment
