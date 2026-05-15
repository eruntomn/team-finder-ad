from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .validators import validate_github_url, validate_phone

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput, validators=[validate_password]
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput, label='Подтверждение пароля'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Телефон'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают')

        return cleaned_data


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'})
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'avatar',
            'about',
            'phone',
            'github_url',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия'}),
            'about': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'О себе'}
            ),
            'phone': forms.TextInput(
                attrs={'placeholder': 'Телефон (8XXXXXXXXXX или +7XXXXXXXXXX)'}
            ),
            'github_url': forms.URLInput(
                attrs={'placeholder': 'https://github.com/username'}
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        user_id = self.instance.id if self.instance else None

        phone = validate_phone(phone)

        if (
            phone
            and User.objects.exclude(id=user_id).filter(phone=phone).exists()
        ):
            raise forms.ValidationError(
                'Пользователь с таким номером телефона уже существует'
            )

        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        return validate_github_url(url)
