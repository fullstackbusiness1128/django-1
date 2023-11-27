from django import forms
from django.contrib.auth import get_user_model
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.core.validators import RegexValidator

from User.token import account_activation_token

User = get_user_model()


class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'password')
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
            'card_number': 'Card Number',
            'expiration_date': 'Expiration Date',
            'cvc': 'Card Code',
            'zip_code': 'Zip Code'
        }
        widgets = {
            'password': forms.PasswordInput(),
        }

    confirm_password = forms.CharField(widget=forms.PasswordInput())

    # agree_tos = forms.BooleanField(label="I agree to <a href='/terms'>Leader Pact Terms</a>")

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("password and confirm_password does not match")


class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    fields = ('email', 'password')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
            'linkedin': 'LinkedIn',
        }


class PasswordTokenForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    uid = forms.CharField(max_length=100)
    token = forms.CharField(max_length=100)

    def verify_token(self, uid, token):
        uid = force_text(urlsafe_base64_decode(uid))
        try:
            user = User.objects.get(email=uid)
            check = account_activation_token.check_token(user, token)
            if not check:
                raise forms.ValidationError({"error": "Token Expired"})
            return user
        except User.DoesNotExist:
            raise forms.ValidationError({'error': 'User with does not exist'})

    def clean(self):
        if self.data['password'] != self.data['confirm_password']:
            raise forms.ValidationError({"error": "Password did not match"})
        response = self.verify_token(self.data['uid'], self.data['token'])
        return response


class EmployerSignupForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100)
    company = forms.CharField(label="Company", max_length=100)
    company_email = forms.EmailField(label="Company Email")
    linkedin_url = forms.URLField(label="Your Linkedin URL", validators=[RegexValidator(
        '^(http(s)?:\/\/)?([\w]+\.)?linkedin\.com\/(pub|in|profile)\/[\w]+(\/)?')])
