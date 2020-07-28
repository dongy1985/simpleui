from django.db import models

# Create your models here.
from common.const import const


# コードマスタ
class CodeMst(models.Model):
    # 大分類コード
    cd = models.CharField(max_length=3, verbose_name="大分類コード", help_text='数字で３桁入力してください.',
                          null=False, blank=False, db_index=True)
    # 大分類名
    cdNm = models.CharField(max_length=20, verbose_name="大分類名", help_text='20文字まで入力してください.',
                            null=False, blank=False)
    # 小分類コード
    subCd = models.CharField(max_length=3, verbose_name="小分類コード", help_text='数字で３桁まで入力してください.',
                             null=False, blank=False)
    # 小分類名
    subNm = models.CharField(max_length=20, verbose_name="小分類名", help_text='20文字まで入力してください.',
                             null=False, blank=False)
    # 適用状態
    delFlg_choices = (
        (const.DEL_FLG_0, '有効'),
        (const.DEL_FLG_1, '無効'),
    )
    delFlg = models.CharField(verbose_name="適用状態", choices=delFlg_choices, max_length=1, default=const.DEF_DEL_FLG)
    # 登録日付
    createTime = models.DateTimeField(verbose_name='登録日付', auto_now=True)
    # 更新日付
    updateTime = models.DateTimeField(verbose_name='更新日付', auto_now=True)

    class Meta:
        verbose_name = "コード"
        verbose_name_plural = "コード管理"

    def __str__(self):
        return self.cd


# 座標マスタ
class CrdMst(models.Model):
    # テンプレート分類
    tplType_choices = CodeMst.objects.filter(cd=const.TEMPLATE_TYPE, delFlg=const.DEL_FLG_0).\
        values_list('subCd', 'subNm').order_by('subCd')
    tplType = models.CharField(verbose_name="テンプレート分類", max_length=3, choices=tplType_choices,
                              null=False, blank=False, db_index=True, default=const.TPL_XLS)
    # 座標分類
    crdDiv_choices = CodeMst.objects.filter(cd=const.CRD_DIV_CD, delFlg=const.DEL_FLG_0).\
        values_list('subCd', 'subNm').order_by('subCd')
    crdDiv = models.CharField(verbose_name="座標分類", max_length=3, choices=crdDiv_choices,
                              null=False, blank=False, db_index=True, default=const.CRD_DIV_H)
    # 項目名
    itemNm = models.CharField(verbose_name="項目名", max_length=60, null=False, blank=False, help_text='20文字まで入力してください.')
    # 項目順
    itemSort = models.IntegerField(verbose_name="項目順", null=False, blank=False, help_text='数字で３桁まで入力してください.')
    # 横座標
    crdX = models.IntegerField(verbose_name="横座標", null=False, blank=False, help_text='数字で入力してください.')
    # 縦座標
    crdY = models.IntegerField(verbose_name="縦座標", null=False, blank=False, help_text='数字で入力してください.')
    # 固定文言
    defVal = models.CharField(verbose_name="固定文言", max_length=60, help_text='固定文言を設定してください.',
                              null=True, blank=True)
    # 備考文言1
    cmnt1 = models.TextField(verbose_name="備考1", max_length=60, help_text='60文字まで入力してください.',
                             null=True, blank=True)
    # 備考文言2
    cmnt2 = models.TextField(verbose_name="備考2", max_length=60, help_text='60文字まで入力してください.',
                             null=True, blank=True)
    # 適用状態
    delFlg_choices = CodeMst.objects.filter(cd=const.DEL_STATUS_CD, delFlg=const.DEL_FLG_0).\
        values_list('subCd', 'subNm').order_by('subCd')
    delFlg = models.CharField(verbose_name="適用状態", choices=delFlg_choices, max_length=1, default=const.DEF_DEL_FLG)
    # 登録日付
    createTime = models.DateTimeField(verbose_name='登録日付', auto_now=True)
    # 更新日付
    updateTime = models.DateTimeField(verbose_name='更新日付', auto_now=True)

    class Meta:
        verbose_name = "座標"
        verbose_name_plural = "座標管理"

    def __str__(self):
        return self.crdDiv
