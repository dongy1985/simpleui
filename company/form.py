from django import forms

# 社員情報フォーム
class EmployeeAdminForm(forms.ModelForm):
    def clean(self):
        return self.cleaned_data
