from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=CustomUser.Role.choices,
        initial=CustomUser.Role.CONSUMER,
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. 9876543210', 'class': 'form-control'})
    )
    village_or_city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Angara or Ranchi', 'class': 'form-control'})
    )
    district = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Ranchi', 'class': 'form-control'})
    )
    preferred_language = forms.ChoiceField(
        choices=[
            ('Hindi', 'हिंदी (Hindi)'),
            ('English', 'English'),
            ('Bengali', 'বাংলা (Bengali)'),
            ('Santhali', 'ᱥᱟᱱᱛᱟᱲᱤ (Santhali)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'role',
            'village_or_city',
            'district',
            'state',
            'pincode',
            'preferred_language',
        )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError("An account with this phone number is already registered.")
        return phone


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username or Phone",
        widget=forms.TextInput(attrs={'placeholder': 'Enter username', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'form-control'})
    )
