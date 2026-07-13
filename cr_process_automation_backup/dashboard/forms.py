from django import forms
from .models import TaskRun


class TaskUploadForm(forms.ModelForm):
    class Meta:
        model = TaskRun
        fields = ['uploaded_template']
        widgets = {
            'uploaded_template': forms.ClearableFileInput(attrs={'class': 'file-input'})
        }
        
class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()