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