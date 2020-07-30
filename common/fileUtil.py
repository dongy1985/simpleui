import time, datetime
import shutil
import openpyxl 
import os
import math

from django.contrib import admin, messages
from django.db import transaction
from django.shortcuts import render
from django.contrib.admin import actions
from django.urls import reverse
from django.contrib import admin
from django.utils.encoding import escape_uri_path
from django.db.models import Q

from attendance.models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from common.models import *
from company.models import *
from common.const import const



def export(queryset, folder_name):
    #temp id
    tempId = ''
    #tempYM
    tempYM = ''
    temp_queryset = None
    #querysetFilter
    for obj in queryset:
        workYM = obj.date.strftime('%Y-%m')
        if obj.user_id != tempId or workYM != tempYM:
            temp_queryset = queryset.filter(
                Q(user_id=obj.user_id)
                &Q(date__startswith=workYM)
            )
            #call make Excel
            mkExcel(temp_queryset, folder_name)
            #更新临时数据
            tempId = obj.user_id
            tempYM = workYM
            queryset = queryset.filter(
                ~(Q(user_id=obj.user_id)
                &Q(date__startswith=workYM))
            )
            return export(queryset=queryset, folder_name=folder_name)

def copyExl(folder_name, userName, objYear, objMonth):
    fileName = const.DIR + folder_name + const.FILESTART + userName + const.UNDERLINE + str(objYear) + str(objMonth) + const.XLSM
    shutil.copyfile(const.TEMPLATEPATH, fileName)
    return fileName

def mkExcel(queryset, folder_name):
    # get data
    for obj in queryset:
        userName = obj.name
        objMonth = obj.date.month
        objYear = obj.date.year
    # copy
    fileName = copyExl(folder_name, userName, objYear, objMonth)
    # book = openpyxl.load_workbook(fileName)
    book = openpyxl.load_workbook(fileName, keep_vba=True)
    sheet = book.get_sheet_by_name(const.SHEET)

    # head data write
    headMst = CrdMst.objects.filter(tplType=const.TPL_XLS, crdDiv=const.CRD_DIV_H, delFlg=const.DEL_FLG_0).\
    values_list('crdY', 'crdX', 'defVal').order_by('itemSort')
    for obj in queryset:
        userNumber = Employee.objects.get(user=obj.user_id).empNo
        userName = obj.name
        objMonth = obj.date.month
        objYear = obj.date.year
        userId = Employee.objects.get(user=obj.user_id).id
        #現場
        if len(WorkSiteDetail.objects.filter(member_id=userId).values('manager_id')) != 0:
            temp_Site_id = WorkSiteDetail.objects.get(member_id=userId).manager_id
            siteNumber = WorkSite.objects.get(id=temp_Site_id).site_number
            projectName = WorkSite.objects.get(id=temp_Site_id).project_name
            managerId = WorkSite.objects.get(id=temp_Site_id).manager_id
            managerNumber = Employee.objects.get(id=managerId).name
    # 社員番号
    sheet.cell(headMst[0][0], headMst[0][1], userNumber)
    # 氏名
    sheet.cell(headMst[1][0], headMst[1][1], userName)
    # 報告月
    sheet.cell(headMst[2][0], headMst[2][1], str(objYear) + '/' + str(objMonth) + '/1')
    # 発注番号
    sheet.cell(headMst[3][0], headMst[3][1], siteNumber)
    # 案件名
    sheet.cell(headMst[4][0], headMst[4][1], projectName)
    # 責任者名
    sheet.cell(headMst[5][0], headMst[5][1], managerNumber)

    # duty data write
    dataMst = CrdMst.objects.filter(tplType=const.TPL_XLS, crdDiv=const.CRD_DIV_D, delFlg=const.DEL_FLG_0).\
        values_list('crdY', 'crdX', 'defVal').order_by('itemSort')
    data_row = dataMst[0][0]
    for obj in queryset:
        # #duty_status
        # duty_status = CodeMst.objects.get(cd=const.DUTY_TYPE, subCd=obj.duty, delFlg=const.DEL_FLG_0).subNm
        # sheet.cell(data_row + obj.date.day, dataMst[0][1], duty_status)
        #start_time
        sheet.cell(data_row + obj.date.day, dataMst[0][1], obj.start_time)
        #end_time
        sheet.cell(data_row + obj.date.day, dataMst[1][1], obj.end_time)
        #restTime
        #0.0 -> 00:00
        temp_modf = math.modf(float(obj.rest))
        temp_hour = int(temp_modf[1])
        temp_minute = int(temp_modf[0] * 60)
        temp_rest_time = str(temp_hour) + ':' + str(temp_minute) 
        # end_time = datetime.strptime(temp_rest_time,"%H:%M:%S")
        # end_time = time.strptime("30 Nov 00", "%d %b %y")
        sheet.cell(data_row + obj.date.day, dataMst[2][1], temp_rest_time)
        # #sumTimeS
        # sheet.cell(data_row + obj.date.day, dataMst[4][1], obj.working_time)
        #contents
        sheet.cell(data_row + obj.date.day, dataMst[3][1], obj.contents)
    #save
    book.save(fileName)

