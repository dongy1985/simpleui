from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here
class Apply(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='apply_user', )
    applyName = models.CharField(verbose_name='申請者', max_length=128)
    applyDate = models.DateField(verbose_name='申請日', default=timezone.now)
    totalMoney = models.CharField(verbose_name='定期券運賃(1ヶ月)', max_length=12, default='')

    class Meta:
        verbose_name = "通勤手当"
        verbose_name_plural = "通勤手当"
        permissions = (
            ("commit_button_apply", "Can 提出"),
            ("confirm_button_apply", "Can 承認"),
            ("cancel_button_apply", "Can 取消"),
        )


class Detail(models.Model):
    name = models.ForeignKey(Apply, on_delete=models.CASCADE, verbose_name='申請者', max_length=128, default='')
    trafficMethod = models.CharField(verbose_name='交通機関', max_length=125, default='')
    trafficSectionStart = models.CharField(verbose_name='開始区間', max_length=12, default='')
    trafficSectionEnd = models.CharField(verbose_name='終了区間', max_length=12, default='')
    trafficExpense = models.CharField(verbose_name='金額', max_length=12, default='')

    class Meta:
        verbose_name = "通勤手当明細"
