from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import Complaint

class SignUpForm(UserCreationForm):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('non_teaching', 'Non Teaching Faculty'),
        ('worker', 'Worker'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

class ComplaintForm(forms.ModelForm):
    anonymous = forms.BooleanField(required=False, initial=False, label="Post Anonymously")
    
    class Meta:
        model = Complaint
        fields = ['category', 'description', 'evidence', 'anonymous']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class RatingForm(forms.Form):
    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput(attrs={'type':'range','min':'1','max':'5'}))

# New forms for password reset functionality
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("There is no user registered with this email address.")
        return email

class PasswordResetCodeForm(forms.Form):
    code = forms.CharField(label="4-Digit Code", max_length=4, min_length=4)

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.isdigit():
            raise forms.ValidationError("Code must be numeric.")
        return code

class SetNewPasswordForm(SetPasswordForm):
    # This extends Django’s SetPasswordForm and will be used to reset the password
    pass

