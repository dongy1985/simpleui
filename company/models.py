from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here
from common.const import const
from common.models import CodeMst
import time


class Apply(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='apply_user', )
    applyName = models.CharField(verbose_name='申請者', max_length=30)
    applyDate = models.DateField(verbose_name='申請日', default=timezone.now)
    totalMoney = models.IntegerField(verbose_name='定期券運賃(1ヶ月)', default='')
    # 状態
    status_list = CodeMst.objects.filter(cd=const.WORK_TYPE).values_list('subCd', 'subNm').order_by('subCd')
    traffic_status = models.CharField(choices=status_list, verbose_name='状態', max_length=3,
                                      default=const.WORK_TYPE_small_0)

    class Meta:
        verbose_name = "通勤手当"
        verbose_name_plural = "通勤手当"
        permissions = (
            ("commit_button_apply", "Can 提出"),
            ("confirm_button_apply", "Can 承認"),
            ("cancel_button_apply", "Can 取消"),
        )


class Detail(models.Model):
    apply = models.ForeignKey(Apply, on_delete=models.CASCADE, verbose_name='申請者', max_length=128, default='')
    trafficMethod = models.CharField(verbose_name='交通機関', max_length=125, default='')
    trafficSectionStart = models.CharField(verbose_name='開始区間', max_length=12, default='')
    trafficSectionEnd = models.CharField(verbose_name='終了区間', max_length=12, default='')
    trafficExpense = models.IntegerField(verbose_name='金額', default='')

    class Meta:
        verbose_name = "通勤手当明細"


class Employee(models.Model):
    name = models.CharField(max_length=30, verbose_name='社員名前', null=False, blank=False, db_index=True)

    empNo = models.CharField(verbose_name='社員番号', max_length=3, null=False, blank=False)

    gender_choices = CodeMst.objects.filter(cd=const.GENDER_CD).values_list('subCd', 'subNm').order_by('subCd')
    gender = models.CharField(max_length=3, choices=gender_choices, verbose_name='性别', default=const.GENDER_DEF)

    birthday = models.DateField(verbose_name='生年月日')

    email = models.EmailField(max_length=120, verbose_name='メールアドレス')

    # 自宅郵便番号
    zipCode = models.CharField(verbose_name='自宅郵便番号', max_length=7, null=False, blank=False,
                               help_text='自宅郵便番号を7桁入力してください.例：1010031')

    homeAddr = models.TextField(max_length=360, verbose_name='住所')

    phone = models.CharField(max_length=11, verbose_name='電話番号')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=False, null=True, verbose_name='UserId',
                             db_index=True)

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


class Expenditure(models.Model):
    name = models.CharField(max_length=const.NAME_LENGTH, verbose_name='資産名')

    buy_date = models.DateField(verbose_name='購入日付', default=time.strftime("%Y-%m-%d"))

    unit_price = models.IntegerField(verbose_name='単価')

    number = models.IntegerField(verbose_name='数量', default=1)

    total_price = models.IntegerField(verbose_name='合計金額')

    note = models.TextField(max_length=const.TEXT_LENGTH, verbose_name='備考', default='なし')

    class Meta:
        verbose_name = "資産合計"
        verbose_name_plural = "資産合計"

    def __int__(self):
        return self.name


class Statement(models.Model):
    name = models.ForeignKey(Expenditure, on_delete=models.CASCADE, verbose_name='資産名', max_length=const.NAME_LENGTH,
                             default='')
    name_code = models.CharField(verbose_name='資産番号', max_length=const.NAME_LENGTH, default='')
    configure = models.CharField(verbose_name='明細', max_length=const.TEXT_LENGTH, default='')

    class Meta:
        verbose_name = "資産合計明細"


class Manage(models.Model):
    name_code = models.CharField(max_length=const.NAME_LENGTH, verbose_name='資産番号')

    kind = models.CharField(max_length=const.NAME_LENGTH, verbose_name='分類')

    name = models.CharField(max_length=const.NAME_LENGTH, verbose_name='名称')

    permission = models.BooleanField(verbose_name='借出可否', default=False)

    note = models.TextField(max_length=const.TEXT_LENGTH, verbose_name='備考', default='なし')

    class Meta:
        verbose_name = "資産状態"
        verbose_name_plural = "資産状態"

    def __int__(self):
        return self.id


class Lend(models.Model):
    name_code = models.ForeignKey(Manage, on_delete=models.SET_NULL, blank=False, null=True, verbose_name='資産番号',
                                  db_index=True)

    real_code = models.CharField(max_length=const.NAME_LENGTH, verbose_name='番号')

    kind = models.CharField(max_length=const.NAME_LENGTH, verbose_name='分類')

    name = models.CharField(max_length=const.NAME_LENGTH, verbose_name='名称')

    worker_number = models.CharField(max_length=const.TEXT_LENGTH)

    user_name = models.CharField(max_length=const.NAME_LENGTH, verbose_name='借出対象')

    apply_time = models.CharField(max_length=const.NAME_LENGTH, verbose_name='申請提出日付',
                                  default=time.strftime("%Y-%m-%d"))

    lend_time = models.CharField(max_length=const.NAME_LENGTH, verbose_name='仮定借出日付', default=time.strftime("%Y-%m-%d"))

    lend_truetime = models.CharField(max_length=const.NAME_LENGTH, verbose_name='実際借出日付', default='未定')

    back_time = models.CharField(max_length=const.NAME_LENGTH, verbose_name='仮定返済日付', default=time.strftime("%Y-%m-%d"))

    back_truetime = models.CharField(max_length=const.NAME_LENGTH, verbose_name='実際返済日付', default='未定')

    lend_reason = models.CharField(max_length=const.TEXT_LENGTH, verbose_name='用途')

    note = models.TextField(max_length=const.TEXT_LENGTH, verbose_name='備考', default='なし')

    lend_status_choices = CodeMst.objects.filter(cd=const.BIG_STATUS).values_list('subCd',
                                                                                  'subNm').order_by(
        'subCd')

    lend_status = models.CharField(max_length=const.NAME_LENGTH, choices=lend_status_choices, verbose_name='申請借出状態'
                                   , default=const.LEND_STATUS)

    class Meta:
        verbose_name = "資産借出申請"
        verbose_name_plural = "資産借出申請"
        permissions = (
            ("apply_lend", "Can apply 資産借出申請"),
        )

    def __int__(self):
        return self.name_code
