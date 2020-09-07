from django.db import models

# Create your models here.
from django.utils import timezone
from common.const import const
from company.models import *

# 障害管理.
class Obstacle(models.Model):
    # 提出者
    user = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=False, null=True, verbose_name='提出者',
                               db_index=True)
    # 提出日付
    createTime = models.DateField('提出日付', default=timezone.now)
    # 障害対象機能_choices
    object_choices = (
        ('1', '現場管理 画面'),
        ('2', '現場管理 を追加/修正'),
        ('3', '社員情報 画面'),
        ('4', '社員情報 を追加/修正'),
        ('5', '立替金　画面'),
        ('6', '立替金 を追加/修正'),
        ('7', '資産管理　画面'),
        ('8', '資産管理 を追加/修正'),
        ('9', '資産貸出申請　画面'),
        ('10', '資産貸出申請 を追加/修正'),
        ('11', '通勤手当　画面'),
        ('12', '通勤手当 を追加/修正'),
        ('13', '勤務管理　画面'),
        ('14', '勤務管理 を追加/修正'),
        ('15', '勤務統計　画面'),
    )
    objectName = models.CharField(max_length=3, choices=object_choices, verbose_name='障害対象機能')
    # 障害内容
    contents = models.TextField(max_length=300, verbose_name='内容')
    # 対応状態
    status_choices = (
        ('0', '起票中'),
        ('1', '対応中'),
        ('2', '対応済'),
    )
    status = models.CharField(verbose_name="対応状態", choices=status_choices, max_length=1, default=0)
    # 対応者
    fixUser_choices = (
        ('0', ''),
        ('1', '于氷清'),
        ('2', '張忠玉'),
        ('3', '陳思達'),
    )
    fixUser = models.CharField(verbose_name="対応者", choices=fixUser_choices, max_length=1, default=0)
    # 対応内容
    fixContents = models.TextField(max_length=300, blank=True, null=True, verbose_name='対応内容')
    # 対応日付
    fixTime = models.DateTimeField(verbose_name='対応日付', auto_now=True)

    class Meta:
        verbose_name = "障害"
        verbose_name_plural = "障害管理"

    def short_contents(self):
        if len(str(self.contents)) > 60:
            return '{}...'.format(str(self.contents)[0:60])
        else:
            return str(self.contents)
    short_contents.allow_tags = True
    short_contents.short_description = '障害内容'

