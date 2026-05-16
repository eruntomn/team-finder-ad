import re

from django.core.exceptions import ValidationError

from .constants import GITHUB_URL_PREFIX, PHONE_REGEX, RUSSIAN_COUNTRY_CODE


def validate_phone(phone):
    if not phone:
        return phone

    if phone.startswith('8'):
        phone = RUSSIAN_COUNTRY_CODE + phone[1:]
    elif phone.startswith(RUSSIAN_COUNTRY_CODE):
        pass
    else:
        raise ValidationError(
            f'Номер телефона должен быть в формате 8XXXXXXXXXX или {RUSSIAN_COUNTRY_CODE}XXXXXXXXXX'
        )

    if not re.match(PHONE_REGEX, phone):
        raise ValidationError(
            'Номер телефона должен содержать 11 цифр после +7'
        )

    return phone


def validate_github_url(url):
    if url and not url.startswith(GITHUB_URL_PREFIX):
        raise ValidationError(
            f'Ссылка должна вести на GitHub ({GITHUB_URL_PREFIX}username)'
        )
    return url
