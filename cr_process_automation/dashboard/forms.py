import re

from django import forms


class TwoFactorAuthForm(forms.Form):
    two_factor_code = forms.CharField(
        max_length=6,
        min_length=6,
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


class NiamCredentialsForm(forms.Form):
    """Form for a user to update their own NIAM OLM ID and NIAM Password."""

    niam_olm_id = forms.CharField(
        max_length=100,
        required=True,
        label="NIAM OLM ID",
        widget=forms.TextInput(attrs={
            "class": "niam-cred-input",
            "placeholder": "Enter your NIAM OLM ID",
            "autocomplete": "off",
            "maxlength": "100",
        }),
        error_messages={
            "required": "NIAM OLM ID is required.",
            "max_length": "NIAM OLM ID must be 100 characters or fewer.",
        },
    )
    niam_password = forms.CharField(
        max_length=128,
        min_length=8,
        required=True,
        label="NIAM Password",
        widget=forms.PasswordInput(attrs={
            "class": "niam-cred-input",
            "placeholder": "Enter your NIAM password",
            "autocomplete": "new-password",
            "maxlength": "128",
        }),
        error_messages={
            "required": "NIAM Password is required.",
            "min_length": "NIAM Password must be at least 8 characters.",
            "max_length": "NIAM Password must be 128 characters or fewer.",
        },
    )
    confirm_niam_password = forms.CharField(
        max_length=128,
        min_length=8,
        required=True,
        label="Confirm NIAM Password",
        widget=forms.PasswordInput(attrs={
            "class": "niam-cred-input",
            "placeholder": "Re-enter your NIAM password",
            "autocomplete": "new-password",
            "maxlength": "128",
        }),
        error_messages={
            "required": "Please confirm your NIAM Password.",
            "min_length": "Confirm password must be at least 8 characters.",
        },
    )

    _OLM_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{3,100}$")
    _PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,128}$")

    def clean_niam_olm_id(self):
        value = (self.cleaned_data.get("niam_olm_id") or "").strip()
        if not value:
            raise forms.ValidationError("NIAM OLM ID is required.")
        if not self._OLM_ID_PATTERN.match(value):
            raise forms.ValidationError(
                "NIAM OLM ID must be 3-100 characters and may only contain "
                "letters, digits, dots, underscores, or hyphens (no spaces)."
            )
        return value

    def clean_niam_password(self):
        value = self.cleaned_data.get("niam_password") or ""
        if not value:
            raise forms.ValidationError("NIAM Password is required.")
        if not self._PASSWORD_PATTERN.match(value):
            raise forms.ValidationError(
                "NIAM Password must be 8-128 characters and include at least "
                "one letter and one digit."
            )
        return value

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("niam_password")
        confirm = cleaned_data.get("confirm_niam_password")
        if password and confirm and password != confirm:
            self.add_error(
                "confirm_niam_password",
                "NIAM Password and Confirm NIAM Password do not match.",
            )
        return cleaned_data
