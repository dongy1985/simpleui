from django.db import models
from django.conf import settings
# Create your models here.
from time import timezone
from django.utils import timezone
from common.const import const
from common.models import *

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
        verbose_name = "勤務"
        verbose_name_plural = "勤務管理"
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