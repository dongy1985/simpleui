from django.contrib import admin

# Register your models here.

from common.models import CrdMst, CodeMst


# Register your models here.
@admin.register(CodeMst)
class CodeMstAdmin(admin.ModelAdmin):

    #　明細エリア
    list_display = ('cd', 'cdNm', 'subCd', 'subNm')
    # １ページの件数
    list_per_page = 15

    # 検索エリア
    list_filter = ('cd', 'cdNm', 'subCd', 'subNm')

    # ソート順
    ordering = ('-cd', 'subCd')


# Register your models here.
@admin.register(CrdMst)
class CrdMstAdmin(admin.ModelAdmin):

    # 明細エリア
    list_display = ('crdDiv', 'itemNm', 'itemSort', 'crdX', 'crdY', 'defVal', 'cmnt1')

    # １ページの件数
    list_per_page = 15

    # 検索エリア
    list_filter = ('crdDiv', 'itemNm')

    # ソート順
    ordering = ('crdDiv', 'itemSort')
