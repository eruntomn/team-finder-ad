from django.db import models

from users.models import User


class Project(models.Model):
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Открыт'),
        (STATUS_CLOSED, 'Закрыт'),
    ]

    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Владелец',
    )
    participants = models.ManyToManyField(
        User,
        blank=True,
        related_name='participating_projects',
        verbose_name='Участники',
    )
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ('-created_at',)

    def __str__(self):
        return self.title
