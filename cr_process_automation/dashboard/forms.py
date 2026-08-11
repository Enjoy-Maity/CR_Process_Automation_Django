from django import forms

class TwoFactorAuthForm(forms.Form):
    two_factor_code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 6-digit 2FA'}),
        required=True,
        label="2FA Code"
    )
    task_id = forms.CharField(widget=forms.HiddenInput(), required=True)

class PasswordAuthForm(forms.Form):
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        }),
        required=True,
        label="Password"
    )
    task_id = forms.CharField(widget=forms.HiddenInput(), required=True)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)