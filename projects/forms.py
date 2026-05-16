from django import forms

from .constants import GITHUB_URL_PREFIX
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'github_url', 'status']
        widgets = {
            'title': forms.TextInput(
                attrs={'placeholder': 'Название проекта'}
            ),
            'description': forms.Textarea(
                attrs={'rows': 5, 'placeholder': 'Описание проекта'}
            ),
            'github_url': forms.URLInput(
                attrs={'placeholder': 'https://github.com/username/repo'}
            ),
            'status': forms.Select(choices=Project.STATUS_CHOICES),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url and not url.startswith(GITHUB_URL_PREFIX):
            raise forms.ValidationError(
                f'Ссылка должна вести на GitHub ({GITHUB_URL_PREFIX}...)'
            )
        return url
