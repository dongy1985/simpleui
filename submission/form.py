import time

from django import forms
from .models import *
from datetime import *

class AttendanceAdminForm(forms.ModelForm):
    def clean(self):
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        rest = self.cleaned_data.get('rest')

        # 実働時間计算
        if end_time == None :
            raise forms.ValidationError({'end_time':'24:00以降は翌日の時刻に入力してください、例：30:00->06:00'})
        temp_end_time = datetime.strptime(str(end_time),"%H:%M:%S")
        sumTime1 = temp_end_time - timedelta(hours=start_time.hour,minutes=start_time.minute,seconds=start_time.second)
        sum_hour = sumTime1.hour
        sum_minute = sumTime1.minute
        if sum_minute != 0:
            sum_hour_dcm = sum_minute / 60
        else:
            sum_hour_dcm = 0
        sumTime2 = sum_hour + sum_hour_dcm
        float_rest = float(rest)
        #休憩時間の制御
        sumTime3 = sumTime2 - float_rest
        if sumTime3 < 0:
            raise forms.ValidationError({'rest':'休憩時間を修正してください'})

        return self.cleaned_data


class ApplyDutyAmountAdminForm(forms.ModelForm):
    # form側からrequestを取得
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ApplyDutyAmountAdminForm, self).__init__(*args, **kwargs)

    def clean(self):
        # requestのpathを取得
        vpath = self.request.path
        # 取得されたrequestのpathによって「通勤手当を追加」画面（vpathにaddが含まれる場合）かどうかを判断
        if "add" in vpath:
            # ログインユーザー取得
            user = self.request.user
            # 申請日
            applyDate = self.cleaned_data.get('applyDate')
            # 申請者
            applyName = Employee.objects.get(user=user).name
            # この申請者と申請日を持ったレコードがDBに存在するかをサーチ
            queryset = ApplyDutyAmount.objects.filter(applyDate=applyDate, user=user).order_by('applyDate')
            # この申請者と申請日を持ったレコードがDBに存在する場合、重複チェックのエラーメッセージを表示
            for obj in queryset:
                strDate = applyDate.strftime("%Y年%m月%d日")
                if applyDate == obj.applyDate and applyName == obj.applyName:
                    raise forms.ValidationError({'applyDate': obj.applyName + 'さんの' + strDate + 'の通勤手当記録は既に存在します，修正してください。'})
            return self.cleaned_data
        else:
            return self.cleaned_data

# 立替金
class ExpenseReturnAdminForm(forms.ModelForm):
    # form側からrequestを取得
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ExpenseReturnAdminForm, self).__init__(*args, **kwargs)

    def clean(self):
        # requestのpathを取得
        vpath = self.request.path
        # ログインユーザー取得
        user = self.request.user
        # 申請日
        applyDate = self.cleaned_data.get('applydate')
        # 申請者
        applyName = Employee.objects.get(user=user).name
        # この申請者と申請日を持ったレコードがDBに存在するかをサーチ
        queryset = ExpenseReturn.objects.filter(applydate=applyDate, user=user).order_by('applydate')

        # 取得されたrequestのpathによって「立替金を追加」画面（vpathにaddが含まれる場合）かどうかを判断
        if "add" in vpath:
            # この申請者と申請日を持ったレコードがDBに存在する場合、重複チェックのエラーメッセージを表示
            for obj in queryset:
                strDate = applyDate.strftime("%Y年%m月%d日")
                if applyDate == obj.applydate and applyName == obj.applyer:
                    raise forms.ValidationError(obj.applyer + 'さんの' + strDate + 'の立替金記録は既に存在します，修正してください。')
            return self.cleaned_data
        else:
            return self.cleaned_data

# 資産貸出
class AssetLendAdminForm(forms.ModelForm):
    def clean(self):
        lend_time = self.cleaned_data.get('lend_time')
        back_time = self.cleaned_data.get('back_time')
        if lend_time > back_time:
            raise forms.ValidationError('貸出予定日は返却予定日より遅い，貸出予定日を修正してください。')
        return self.cleaned_data
