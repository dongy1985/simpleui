import shutil
import time, datetime
import openpyxl
import os
from django.contrib import admin, messages
from django.db import transaction
from django.shortcuts import render
from django.contrib.admin import actions
from django.urls import reverse
from django.contrib import admin
from django.utils.encoding import escape_uri_path
from django.db.models import Q
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from common.models import *
from company.models import *
from common.const import const
from copy import copy
from aggregation.models import *


def export(queryset, folder_name, fileName, count):
    # copy
    if count == 0:
        fileName = copyExl(folder_name, '年度集記表')
    else:
        fileName = fileName

    # querysetFilter
    for obj in queryset:
        workYM = obj.attendance_YM.strftime('%Y-%m')
        temp_queryset = Aggregation.objects.filter(
            Q(attendance_YM__startswith=workYM)
        )
        # mkExcel
        mkExcel(temp_queryset, fileName, count)
        count += 1
        queryset = queryset.filter(~(Q(attendance_YM__startswith=workYM)))
        return export(queryset=queryset, folder_name=folder_name, fileName=fileName, count=count)


def copyExl(folder_name, userName):
    fileName = const.DIR + folder_name + const.FILESTART + userName + const.XLS
    shutil.copyfile(const.YEAR_TEMPLATEPATH, fileName)
    return fileName


def mkExcel(queryset, fileName, count):
    # コピー先ファイル名の取得
    book = openpyxl.load_workbook(fileName)
    # コピー先シート名の取得
    sheet = book.get_sheet_by_name(const.SHEET_YEAR)

    # data write
    row = 0
    i = 1
    j = 1

    for obj in queryset:
        # 行のコピー
        j = j + 1
        for a in range(1, 9):
            e = sheet.cell(row=j+1, column=a)
            sheet[e.coordinate]._style = sheet.cell(row=3, column=a)._style

        # 列のコピー
        for i in range(3, 9):
            e = sheet.cell(row=j+1, column=i + 6*count)
            sheet[e.coordinate]._style = sheet.cell(row=3, column=i)._style

            if j == 2:
                # 月分の列を定義
                e1 = sheet.cell(row=1, column=i + 6*count)
                sheet[e1.coordinate]._style = sheet.cell(row=1, column=i)._style
                # コピー元の列を定義
                copy = sheet.cell(row=2, column=i).value
                sheet.cell(row=2, column=i + 6*count, value=copy)
                e2 = sheet.cell(row=2, column=i + 6*count)
                sheet[e2.coordinate]._style = sheet.cell(row=2, column=i)._style
        sheet.merge_cells(const.SERU[count])

        # 社員番号
        aggEmpNo = obj.empNo
        # 社員名前
        aggName = obj.name
        # 実働時間
        aggWorkTime = obj.working_time
        # 出勤日数
        aggAttendCount = obj.attendance_count
        # 欠勤日数
        aggAbsCount = obj.absence_count
        # 年休日数
        aggAnnLeave = obj.annual_leave
        # 休出日数
        aggRestCount = obj.rest_count
        # 遅早退日数
        aggLateCount = obj.late_count
        # 統計年月
        objMonth = obj.attendance_YM.strftime('%Y-%m')

        # write data
        # 報告月
        sheet.cell(1, 3 + count * 6, objMonth)
        if count == 0:
            # 社員番号
            sheet.cell(3 + row, 1 + count * 6, aggEmpNo)
            # 氏名
            sheet.cell(3 + row, 2 + count * 6, aggName)
        # 実働時間
        sheet.cell(3 + row, 3 + count * 6, aggWorkTime)
        # 出勤
        sheet.cell(3 + row, 4 + count * 6, aggAttendCount)
        # 欠勤
        sheet.cell(3 + row, 5 + count * 6, aggAbsCount)
        # 年休
        sheet.cell(3 + row, 6 + count * 6, aggAnnLeave)
        # 休出
        sheet.cell(3 + row, 7 + count * 6, aggRestCount)
        # 遅早退
        sheet.cell(3 + row, 8 + count * 6, aggLateCount)
        row = row + 1
        # save
        book.save(fileName)
