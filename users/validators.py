import re

from django.core.exceptions import ValidationError


def validate_phone(phone):
    if not phone:
        return phone

    if phone.startswith('8'):
        phone = '+7' + phone[1:]
    elif phone.startswith('+7'):
        pass
    else:
        raise ValidationError(
            'Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX'
        )

    if not re.match(r'^\+7\d{10}$', phone):
        raise ValidationError(
            'Номер телефона должен содержать 11 цифр после +7'
        )

    return phone


def validate_github_url(url):
    if url and not url.startswith('https://github.com/'):
        raise ValidationError(
            'Ссылка должна вести на GitHub (https://github.com/username)'
        )
    return url
