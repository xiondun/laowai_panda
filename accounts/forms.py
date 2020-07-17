from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit, Row, Column
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ValidationError


class SignUpForm(UserCreationForm):
    def clean_email(self):
        try:
            email = self.cleaned_data.get('email')
            user = User.objects.get(username=email)
            raise forms.ValidationError('User with this email arleady exist.', code='invalid')
        except User.DoesNotExist:
            return email

    def send_email():
        pass

    class Meta:
        model = User
        fields = ('full_name','email', 'phone' )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        helper = self.helper = FormHelper()
        
        self.fields['email'].widget.attrs['placeholder'] = 'E-mail'
        self.fields['password1'].widget.attrs['placeholder'] = 'password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirmation password'
        self.fields['full_name'].widget.attrs['placeholder'] = 'Full Name'
        self.fields['phone'].widget.attrs['placeholder'] = 'Phone Number'
        helper.form_show_labels = False

class LoginForm(AuthenticationForm):
    AuthenticationForm.error_messages['invalid_login'] =  "Please enter a correct email and password. Note that both fields may be case-sensitive."
    def clean_username(self):
        username = self.data['username']
        if '@' in username:
            try:
                username = User.objects.get(email=username).username
            except ObjectDoesNotExist:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username':self.username_field.verbose_name},
                )
        return username

   
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError('There was a problem with your login.', code='invalid_login')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        helper = self.helper = FormHelper()
        
        self.fields['username'].widget.attrs['placeholder'] = 'E-mail'
        self.fields['password'].widget.attrs['placeholder'] = 'password'
        helper.form_show_labels = False