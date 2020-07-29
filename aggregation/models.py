from django.db import models
from common.models import *
# Create your models here.


class Aggregation(models.Model):
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

    class Meta:
        verbose_name = "勤務レポート"
        verbose_name_plural = "勤務レポート"
        permissions = (
            ("export_button", "Can 導出"),
        )

    def __str__(self):
        return self.name
