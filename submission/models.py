from django.db import models
from django.conf import settings
# Create your models here.
from django.core import validators
from datetime import datetime
from django.contrib.auth.models import User
from time import timezone
from django.utils import timezone
from common.const import const
from common.models import *
from company.models import *
import time

class Attendance(models.Model):
    # 社員名前
    name = models.CharField('社員名前', max_length=20, default=0) 
    # 出勤日付
    date = models.DateField('出勤日付', default=timezone.now)
    # 出勤区分
    duty_status = CodeMst.objects.filter(cd=const.DUTY_TYPE, delFlg=const.DEL_FLG_0).values_list('subCd','subNm').order_by('subCd')
    duty = models.CharField(max_length=5, choices=duty_status, verbose_name='出勤区分', default=const.DEF_DUTY)
    # 開始時刻
    start_time =  models.TimeField('開始時刻',default=const.DEF_STARTTIME, help_text='例：09:00')
    # 終了時刻
    end_time = models.TimeField('終了時刻', default=const.DEF_ENDTIME, help_text='例：18:00')
    # 休憩時間
    rest = models.DecimalField(verbose_name='休憩時間', max_digits=3, decimal_places=1, default=const.DEF_RESTTIME)
    # 実働時間
    working_time = models.DecimalField(verbose_name='実働時間', max_digits=3, decimal_places=1, default=const.DEF_WORKTIME)
    # 作業概要
    contents = models.TextField(max_length=48, verbose_name='作業概要', default='開発作業')
    # 報告区分
    status_c = CodeMst.objects.filter(cd=const.WORK_TYPE, delFlg=const.DEL_FLG_0).values_list('subCd','subNm').order_by('subCd')
    status = models.CharField(max_length=5, choices=status_c, verbose_name='報告区分', default=const.WORK_TYPE_SMALL_0)
    # user id
    user_id = models.CharField(max_length=3, default=const.DEF_USERID)


    class Meta:
        verbose_name = "勤務提出"
        verbose_name_plural = "勤務提出"
        unique_together = ('user_id', 'date')
        permissions = (
            ('commit_button_attendance', 'Can 提出'),
            ('confirm_button_attendance', 'Can 承認'),
            ('export_attendance', 'Can エクスポート'),
        )

# 勤務統計モデル
class DutyStatistics(models.Model):
    # 社員番号
    empNo = models.CharField(verbose_name='社員番号', max_length=3)
    # 社員名前
    name = models.CharField(verbose_name='社員名前', max_length=20, default=0)
    # 統計年月
    attendance_YM = models.DateField(verbose_name='統計年月')
    # 実働時間
    working_time = models.DecimalField(verbose_name='実働時間', max_digits=4, decimal_places=1)
    # 出勤日数
    attendance_count = models.IntegerField(verbose_name='出勤')
    # 欠勤
    absence_count = models.IntegerField(verbose_name='欠勤')
    # 年休
    annual_leave = models.IntegerField(verbose_name='年休')
    # 休出
    rest_count = models.IntegerField(verbose_name='休出')
    # 遅早退
    late_count = models.IntegerField(verbose_name='遅早退')
    # 登録日付
    createTime = models.DateTimeField(verbose_name='登録日付', auto_now=True)
    # 更新日付
    updateTime = models.DateTimeField(verbose_name='更新日付', auto_now=True)

    class Meta:
        verbose_name = "勤務統計"
        verbose_name_plural = "勤務統計"
        permissions = (
            ("export_dutystatistics", "Can エクスポート"),
        )


    def __str__(self):
        return self.name

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
    trafficAmount = models.CharField(verbose_name='金額', max_length=10, default='',
                     validators=[validators.RegexValidator("^\d{1,3}(,\d{3})*$", message='正しい金額を入力してください！')])

    class Meta:
        verbose_name = "通勤手当明細"
        verbose_name_plural = "通勤手当明細"

    def __str__(self):
        return self.trafficMethod

# 資産貸出
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
        verbose_name = "資産貸出"
        verbose_name_plural = "資産貸出"
        permissions = (
            ("manage_assetlend", "Can manage 資産貸出"),
            ("commit_assetlend", "Can 提出"),
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
    status = models.CharField(max_length=3, choices=status_choices, verbose_name='申請状態',
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
    price = models.CharField(verbose_name='金額', max_length=10, default='',
                 validators=[validators.RegexValidator("^\d{1,3}(,\d{3})*$", message='正しい金額を入力してください！')])
    # 使用日付
    usedate = models.DateField(verbose_name='使用日付')

    class Meta:
        verbose_name = "立替金項目明細"
        verbose_name_plural = "立替金項目明細"

    def __str__(self):
        return self.detail_type

