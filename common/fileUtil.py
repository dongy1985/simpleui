import time, datetime
# import xlrd
# import xlwt 
# import xlutils.copy
import shutil
import openpyxl 
import calendar
import os
import zipfile

from django.contrib import admin, messages
from django.db import transaction
from django.shortcuts import render
from django.contrib.admin import actions
from django.urls import reverse
from django.contrib import admin
from django.contrib.auth import get_user
from django.http.response import HttpResponse
from django.http import HttpResponse
from django.contrib.auth import get_permission_codename
from django.utils.encoding import escape_uri_path
from django.db.models import Q
from six.moves import urllib

from attendance.models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from common.models import CodeConst
from common.models import Coordinate
from company.models import Employee
from common.const import const


def export(queryset, folder_name):

    #temp id
    tempId = ''
    #临时年月
    tempYM = ''
    temp_queryset = None
    #对数据进行判断（筛选用户和年月）
    for obj in queryset:
        workYM = obj.date.strftime('%Y-%m')
        if obj.employe_id != tempId or workYM != tempYM:
            #单独抽出该用户的该月数据
            temp_queryset = queryset.filter(
                Q(employe_id=obj.employe_id)
                &Q(date__startswith=workYM)
            )
            #制作该数据的EXCEL
            mkExcel(temp_queryset, folder_name)
            #更新临时数据
            tempId = obj.employe_id
            tempYM = workYM
            queryset = queryset.filter(
                ~(Q(employe_id=obj.employe_id)
                &Q(date__startswith=workYM))
            )
            return export(queryset=queryset, folder_name=folder_name)

def copyExl(folder_name, userName, objYear, objMonth):
    fileName = const.DIR + folder_name + const.FILESTART + userName + const.UNDERLINE + str(objYear) + str(objMonth) + const.XLSX
    shutil.copyfile(const.TEMPLATEPATH, fileName)
    return fileName

def mkExcel(queryset, folder_name):
    # 获取基础信息部分
    for obj in queryset:
        userName = obj.name
        objMonth = obj.date.month
        objYear = obj.date.year
    # 呼出文件复制
    fileName = copyExl(folder_name, userName, objYear, objMonth)
    # 打开excel
    book = openpyxl.load_workbook(fileName)
    sheet = book.get_sheet_by_name(const.SHEET)

    headMst = Coordinate.objects.filter(coorDivision=const.HEAD).\
        values_list('coorY', 'coorX', 'fixedValue').order_by('dspOrder')

    # 写head部分
    for obj in queryset:
        userNumber = Employee.objects.get(user=obj.user).employe_number
        userName = obj.name
        objMonth = obj.date.month
        objYear = obj.date.year
    sheet.cell(headMst[0][0], headMst[0][1], userNumber)
    sheet.cell(headMst[1][0], headMst[1][1], userName)
    sheet.cell(headMst[2][0], headMst[2][1], str(objYear) + '/' + str(objMonth))

    # DUTYwrite（寫勤務部分）
    dataMst = Coordinate.objects.filter(coorDivision=const.DATA).\
        values_list('coorY', 'coorX', 'fixedValue').order_by('dspOrder')
    data_row = dataMst[0][0]
    for obj in queryset:
        #duty_status
        duty_status = CodeConst.objects.get(big_code=const.DUTY_TYPE, small_code=obj.duty).small_name
        sheet.cell(data_row + obj.date.day, dataMst[1][1], duty_status)

        #start_time转换
        sheet.cell(data_row + obj.date.day, dataMst[2][1], obj.start_time)
        #end_time转换
        sheet.cell(data_row + obj.date.day, dataMst[3][1], obj.end_time)

        #restTime转换
        sheet.cell(data_row + obj.date.day, dataMst[4][1], float(obj.rest))

        #sumTimeS转换
        sheet.cell(data_row + obj.date.day, dataMst[5][1], obj.working_time)

        #contents转换
        sheet.cell(data_row + obj.date.day, dataMst[6][1], obj.contents)

    book.save(fileName)

