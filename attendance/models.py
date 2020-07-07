from django.db import models
from django.conf import settings
# Create your models here.
from time import timezone
from django.utils import timezone
from codeTools.models import CodeTools

# Create your models here.

class Duty(models.Model):
    name = models.CharField('社員名前', max_length=20, default=0) 
    date = models.DateField('出勤日付', default=timezone.now)
    duty_status = CodeTools.objects.filter(bigCode='003').values_list('smallCode','smallCodename').order_by('smallCodename')
    duty = models.CharField(max_length=5, choices=duty_status, verbose_name='出勤区分', default='00')
    start_time =  models.TimeField('開始時刻',default='09:00')
    end_time = models.TimeField('終了時刻', default='18:00')
    rest = models.DecimalField(verbose_name='休憩時間', max_digits=3, decimal_places=1, default=1.0)
    working_time = models.DecimalField(verbose_name='実働時間', max_digits=3, decimal_places=1, default=1.5)
    contents = models.TextField(max_length=48, verbose_name='作業概要', default='開発作業')
    status_c = CodeTools.objects.filter(bigCode='005').values_list('smallCode','smallCodename').order_by('smallCodename')
    status = models.CharField(max_length=5, choices=status_c, verbose_name='報告区分', default='00')
    employe_id = models.CharField(max_length=3, default=0)


    class Meta:
        verbose_name = "勤務"
        verbose_name_plural = "勤務管理"
        permissions = (
            ('commit_button_duty', 'Can 提出'),
            ('confirm_button_duty', 'Can 承認'),
            ("export_duty", "Can エクスポート"),
        )