from django.contrib import admin
from obstacle.models import *
from common.custom_filter import DateFieldFilter

# Register your models here.
@admin.register(Obstacle)
class ObstacleAdmin(admin.ModelAdmin):
    # display
    list_display = ('id', 'user', 'createTime', 'objectName', 'short_contents', 'status', 'fixUser', 'fixTime')
    # list
    list_filter = ('status',('createTime', DateFieldFilter))
    # set search
    search_fields = ('contents',)
    # ordering
    ordering = ('id',)
    # 一ページ表示の数
    list_per_page = 20