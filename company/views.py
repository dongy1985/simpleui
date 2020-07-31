from django.shortcuts import render

# Create your views here.
import datetime
from dateutil.relativedelta import relativedelta
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

from company.models import Employee
from common import mailUtil
scheduler = BackgroundScheduler()

scheduler.add_jobstore(DjangoJobStore(), 'default')


# 毎日10時在留期限チェック
@register_job(scheduler, 'cron', id='check', hour=10, minute=1)
def check():
    next_month = datetime.date.today() + relativedelta(months=+1)
    expErrList = []
    # 未来一ヶ月の日期と在留期限の比較
    target_name = Employee.objects.filter(retention_limit=next_month).values()
    for obj in target_name:
        # 社員へメール
        expErrList.append(obj['name'] + 'の在留期限まだ一ヶ月 ')
        employe_name = obj['name']
        employe_mail = obj['email']
        main = employe_name + 'さん、在留期限まだ一ヶ月、ご注意ください'
        mailUtil.retention_mail(employe_name, employe_mail, main)
    if len(expErrList) > 0:
        # 管理者へメール
        employe_name = Employee.objects.get(empNo='001').name
        employe_mail = Employee.objects.get(empNo='001').email
        main = expErrList
        mailUtil.retention_mail(employe_name, employe_mail, main)


# register
register_job(scheduler)
scheduler.start()