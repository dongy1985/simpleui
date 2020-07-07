from django.db import models

# Create your models here.
from common import const


class CodeConst(models.Model):
    big_code = models.CharField(verbose_name='大分類コード', max_length=20)
    big_name = models.CharField(verbose_name='大分類名', max_length=20)
    small_code = models.IntegerField(verbose_name='小分類コード')
    small_name = models.CharField(verbose_name='小分類名', max_length=20)

    class Meta:
        verbose_name = "コード管理"
        verbose_name_plural = "コード管理"

    def __str__(self):
        return self.big_name


class Coordinate(models.Model):
    coorDivision_choices = CodeConst.objects.filter(big_code=const.EXCEL_COORDINATE).\
        values_list('small_code', 'small_name').order_by('small_code')
    coorDivision = models.CharField(max_length=3, verbose_name='座標区分', default='0', choices=coorDivision_choices)
    dspOrder = models.IntegerField(verbose_name='表示順')
    coorName = models.CharField(verbose_name='座標名', max_length=20)
    coorX = models.IntegerField(verbose_name='X座標')
    coorY = models.IntegerField(verbose_name='Y座標')
    fixedValue = models.CharField(verbose_name='固定値', max_length=20, null=True, blank=True)
    remarks = models.CharField(verbose_name='備考', max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Excel座標管理"
        verbose_name_plural = "Excel座標管理"

    def __str__(self):
        return self.coorName


