from django import forms

# 資産貸出
class EmployeeAdminForm(forms.ModelForm):
    def clean(self):
        return self.cleaned_data
