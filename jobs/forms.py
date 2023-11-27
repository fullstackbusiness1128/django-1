from django import forms
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from .models import JobPost, Company, Rating
from django.contrib.auth import get_user_model
from localflavor.us.forms import USStateSelect

from User.token import account_activation_token

User = get_user_model()

class JobAddEditForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = (
        'company_name', 'job_title', 'locations', 'about_role', 'functions', 'skills', 'travel', 'about_company',
        'industry', 'company_type', 'company_age', 'employees', 'salary', 'company',)


class CompanyAddEditForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('name',)


class RatingAddEditForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ('rating',)


class UserListForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())


class PaymentForm(forms.Form):
    card_number = forms.CharField()
    expiration_date = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'MM/YY'}))
    card_code = forms.CharField()
    address = forms.CharField()
    city = forms.CharField()
    state = forms.CharField(widget=USStateSelect())
    zip_code = forms.CharField(max_length=5)


class EmailForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=50)

    def clean_email(self):
        try:
            User.objects.get(email=self.data['email'])
            return self.data['email']
        except User.DoesNotExist:
            raise forms.ValidationError({'error': 'User with {} does not exist'.format(self.email)})
