from behaviors.behaviors import Timestamped
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from core.utils import truncate


class DefaultModel(models.Model):
    """Абстрактная модель по умолчанию."""

    class Meta:
        abstract = True


class TimestampedModel(DefaultModel, Timestamped):
    """Абстрактная модель для моделей с датами."""

    class Meta:
        abstract = True


TimestampedModel._meta.get_field('created').verbose_name = 'дата создания'


class AuthoredModel(TimestampedModel):
    """Абстрактная модель для моделей с авторами текста."""

    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    text = models.TextField('текст', help_text='введите ваш текст')

    class Meta:
        abstract = True
        ordering = ('-created',)

    def __str__(self) -> str:
        return truncate(self.text, settings.TRUNCATION)
