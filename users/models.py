from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from .constants import ABOUT_MAX_LENGTH, NAME_MAX_LENGTH, PHONE_MAX_LENGTH


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        first_name,
        last_name,
        phone,
        password=None,
        **extra_fields,
    ):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        first_name,
        last_name,
        phone,
        password=None,
        **extra_fields,
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(
            email, first_name, last_name, phone, password, **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Email', unique=True)
    first_name = models.CharField('Имя', max_length=NAME_MAX_LENGTH)
    last_name = models.CharField('Фамилия', max_length=NAME_MAX_LENGTH)
    avatar = models.ImageField(
        'Аватар', upload_to='avatars/', blank=True, default=''
    )
    phone = models.CharField('Телефон', max_length=PHONE_MAX_LENGTH)
    github_url = models.URLField('GitHub', blank=True, default='')
    about = models.TextField(
        'О себе', max_length=ABOUT_MAX_LENGTH, blank=True, default=''
    )
    skills = models.ManyToManyField(
        'skills.Skill',
        blank=True,
        related_name='users',
        verbose_name='Навыки',
    )

    is_active = models.BooleanField('Активен', default=True)
    is_staff = models.BooleanField('Персонал', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
