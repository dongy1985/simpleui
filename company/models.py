from datetime import datetime
from django.contrib.auth.models import User
from django.core import validators
from django.db import models
from django.utils import timezone
from common.const import const
from common.models import *
import time

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
    zipCode = models.CharField(verbose_name='自宅郵便番号', max_length=8, null=False, blank=False,
               validators=[validators.RegexValidator("^[0-9]{3}-[0-9]{4}$", message='正しい郵便番号を入力してください！')],
               help_text='自宅郵便番号を7桁半角数字で入力してください.例：101-0031')
    # 住所
    homeAddr = models.TextField(max_length=360, verbose_name='住所')
    # 電話番号
    phone = models.CharField(max_length=13, verbose_name='電話番号',
            validators=[validators.RegexValidator("^0\d{2,3}-\d{4}-\d{4}$", message='正しい電話番号を入力してください！')],
            help_text='自宅郵便番号を11桁半角数字で入力してください.例：070-2100-9009')
    # 在留カード番号
    retention_code = models.CharField(max_length=12, verbose_name='在留カード', null=True, blank=True)
    # 在留カード期限
    retention_limit = models.DateField(verbose_name='在留期限', null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=False, null=True, verbose_name='ログインユーザー',
                             db_index=True, unique=True)
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


# 資産情報
class AssetManage(models.Model):
    # 資産番号
    asset = models.CharField(unique=True, max_length=const.NAME_LENGTH, verbose_name='資産番号',
    validators=[validators.RegexValidator("^[A-Za-z0-9]+$", message='半角英数字で入力してください！')],
                             help_text='半角英数字で入力してください')
    # 分類
    type_choices = CodeMst.objects.filter(cd=const.ASSET_TYPE).values_list('subCd', 'subNm').order_by('subCd')
    type = models.CharField(max_length=const.NAME_LENGTH, choices=type_choices, verbose_name='分類', default=const.ASSET_DEF)

    # 名称
    name = models.CharField(max_length=const.NAME_LENGTH, verbose_name='名称')

    # 貸出可否
    permission = models.BooleanField(verbose_name='貸出可否', default=False)

    # 備考
    note = models.TextField(max_length=const.TEXT_LENGTH, verbose_name='備考', null=True, blank=True)

    class Meta:
        verbose_name = "資産情報"
        verbose_name_plural = "資産情報"

    def __int__(self):
        return self.id

    def __str__(self):
        return self.asset

# 現場情報モデル
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
        verbose_name = "現場情報"
        verbose_name_plural = "現場情報"


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
        unique_together = ('manager', 'member')

    def __int__(self):
        return self.id

    def __str__(self):
        return self.comment
