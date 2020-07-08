import time, datetime
import smtplib

from django.contrib.auth import get_user
from common.models import *
from company.models import *
from common.const import const

from email.mime.text import MIMEText
from email.header import Header
from django.db.models import Q
from django.contrib.auth.models import User, Permission


def sendmail(mailKbn, queryset):
    tempId = ''
    tempYM = ''
    temp_queryset = None
    for obj in queryset:
        workYM = obj.date.strftime('%Y-%m')
        if obj.user_id != tempId:
            employe_name = obj.name
            employe_mail = Employee.objects.get(user=obj.user_id).email
            send(mailKbn, employe_name, employe_mail, temp_queryset)
            tempId = obj.user_id
            queryset = queryset.filter(
                ~(Q(user_id=obj.user_id))
            )
            return sendmail(mailKbn=mailKbn, queryset=queryset)

def send(mailKbn, employe_name, employe_mail, queryset):
    #fromAddrの設定
    from_addr = const.ADMIN_MAIL
    password = const.ADMIN_MAIL_PAS
    smtp_server = 'smtp.gmail.com'

    #toAddr、内容の設定
    main = ''
    Subject = ''
    to_addr, main, Subject = chooseKbn(mailKbn, employe_name, employe_mail)
    msg = MIMEText(main,'plain','utf-8')
 
    msg['From'] = Header(from_addr)
    msg['To'] = Header(to_addr)
    msg['Subject'] = Header(Subject)
    
    server = smtplib.SMTP_SSL(host=smtp_server)
    server.connect(host=smtp_server, port=465)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr.split(','), msg.as_string())
    server.quit()
    print ('success    ' + to_addr)

def chooseKbn(mailKbn, employe_name, employe_mail):

    if mailKbn == const.MAIL_KBN_COMMIT:
        #to_addr
        perm = Permission.objects.get(codename='confirm_button_attendance')  
        users = User.objects.filter(Q(user_permissions=perm) | Q(is_superuser=True)).distinct()
        to_addr = ''
        for obj in users:
            to_addr += Employee.objects.get(user=obj.id).email + ', '
        #main
        main = '承認者さん、お疲れ様です。\n\n' + employe_name +'勤務を提出しました、ご確認お願い致します。\n'
        #Subject
        Subject = employe_name + 'の勤務が提出しました'
        return (to_addr, main, Subject)
    elif mailKbn == const.MAIL_KBN_CANCEL:
        to_addr = employe_mail
        main = employe_name + 'さん、お疲れ様です。\n\n勤務が取消しました、ご確認お願い致します。\n' 
        Subject = employe_name + 'の勤務が承認しました'
        return (to_addr, main, Subject)
    elif mailKbn == const.MAIL_KBN_CONFIRM:
        to_addr = employe_mail
        main = employe_name + 'さん、お疲れ様です。\n\n勤務が承認しました、ご確認お願い致します。\n' 
        Subject = employe_name + 'の勤務が承認しました'
        return (to_addr, main, Subject)
    