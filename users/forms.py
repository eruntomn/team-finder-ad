from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import re
from .models import User

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput, validators=[validate_password])
    password_confirm = forms.CharField(
        widget=forms.PasswordInput, label='Подтверждение пароля')

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'surname': forms.TextInput(attrs={'placeholder': 'Фамилия'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Телефон'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Пользователь с таким email уже существует')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder': 'Email'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'surname': forms.TextInput(attrs={'placeholder': 'Фамилия'}),
            'about': forms.Textarea(attrs={'rows': 4, 'placeholder': 'О себе'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Телефон (8XXXXXXXXXX или +7XXXXXXXXXX)'}),
            'github_url': forms.URLInput(attrs={'placeholder': 'https://github.com/username'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            return phone

        if phone.startswith('8'):
            phone = '+7' + phone[1:]
        elif phone.startswith('+7'):
            pass
        else:
            raise forms.ValidationError(
                'Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX')

        if not re.match(r'^\+7\d{10}$', phone):
            raise forms.ValidationError(
                'Номер телефона должен содержать 11 цифр после +7')

        user_id = self.instance.id if self.instance else None
        if User.objects.exclude(id=user_id).filter(phone=phone).exists():
            raise forms.ValidationError(
                'Пользователь с таким номером телефона уже существует')

        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url:
            if not url.startswith('https://github.com/'):
                raise forms.ValidationError(
                    'Ссылка должна вести на GitHub (https://github.com/username)')
        return url
