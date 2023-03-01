from behaviors.behaviors import Timestamped
from django.contrib.auth import get_user_model
from django.db import models


class DefaultModel(models.Model):
    """Абстрактная модель по умолчанию."""

    class Meta:
        abstract = True


class TimestampedModel(DefaultModel, Timestamped):
    """Абстрактная модель для моделей с датами."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._meta.get_field('created').verbose_name = 'дата создания'
        self._meta.get_field('created').help_text = 'дата создания'
        self._meta.get_field('modified').verbose_name = 'дата изменения'
        self._meta.get_field('modified').help_text = 'дата изменения'

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
