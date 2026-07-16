from django import forms

class TwoFactorAuthForm(forms.Form):
    two_factor_code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 6-digit 2FA'}),
        required=True,
        label="2FA Code"
    )
    task_id = forms.CharField(widget=forms.HiddenInput(), required=True)