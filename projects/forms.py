from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Название проекта'}),
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
        if url:
            if not url.startswith('https://github.com/'):
                raise forms.ValidationError(
                    'Ссылка должна вести на GitHub (https://github.com/...)'
                )
        return url
