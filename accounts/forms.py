from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class LoginForm(forms.ModelForm):
    email = forms.CharField(max_length=60, required=True, label="")
    password = forms.CharField(widget=forms.PasswordInput(), label="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs = {
            "class": "form-control string email optional",
            "autofocus": "autofocus",
            "id": "email",
        }
        self.fields["password"].widget.attrs = {
            "class": "form-control password optional",
            "style": "background: #f7f7ff;",
            "id": "user_password",
        }

    def clean(self):
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Inocorrect email or password")
        user = User.objects.filter(email=email).first()

        if user:
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect password")

        return self.cleaned_data

    class Meta:
        model = User
        fields = ["email", "password"]


class RegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=60, required=True, label="")
    last_name = forms.CharField(max_length=60, required=True, label="")
    email = forms.CharField(max_length=60, required=True, label="")
    password = forms.CharField(
        widget=forms.PasswordInput(), validators=[validate_password], label=""
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs = {
            "class": "form-control string required",
            "id": "user_first_name",
            "data-validate": "true",
        }
        self.fields["last_name"].widget.attrs = {
            "class": "form-control string required",
            "id": "user_last_name",
            "data-validate": "true",
        }
        self.fields["email"].widget.attrs = {
            "class": "form-control string email optional",
            "id": "user_email",
            "data-validate": "true",
        }
        self.fields["password"].widget.attrs = {
            "class": "form-control password optional",
            "id": "user_password",
            "data-validate": "true",
        }

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Incorrect email or password")
        return email

    def clean(self):
        return self.cleaned_data

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]


class ResetPasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    new_password_repeat = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs = {
            "class": "form-control",
            "style": "background: #f7f7ff;",
            "placeholder": "New password",
        }
        self.fields["new_password"].widget.attrs = {
            "class": "form-control",
            "style": "background: #f7f7ff;",
            "placeholder": "New password",
        }
        self.fields["new_password_repeat"].widget.attrs = {
            "class": "form-control",
            "style": "background: #f7f7ff;",
            "placeholder": "Repeat new password",
        }

    def clean_password(self):
        old_password = self.cleaned_data["old_password"]
        new_password = self.cleaned_data["new_password"]
        new_password_repeat = self.cleaned_data["new_password_repeat"]
        if old_password == new_password:
            raise forms.ValidationError("That password already in use")

        if not new_password == new_password_repeat:
            raise forms.ValidationError("Passwords does not match ")

        return new_password

    def clean(self):
        return self.cleaned_data
