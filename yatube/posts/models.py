from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel
from core.utils import truncate
from yatube.settings import TRUNCATION

User = get_user_model()


class Group(models.Model):
    """Модель ORM для хранения групп постов пользователей."""

    title = models.CharField('название', max_length=200)
    slug = models.SlugField('слаг', max_length=200, unique=True)
    description = models.TextField('описание')

    class Meta:
        verbose_name = 'группа постов'
        verbose_name_plural = 'группы постов'

    def __str__(self) -> str:
        return truncate(self.title, TRUNCATION)


class Post(CreatedModel):
    """Модель ORM для хранения постов пользователей."""

    text = models.TextField('текст', help_text='введите текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='группа постов',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        default_related_name = 'posts'
        ordering = ('-pk',)
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        return f'Пост {self.pk}: {truncate(self.text, TRUNCATION)}'


class Comment(CreatedModel):
    """Модель ORM для хранения комментариев пользователей."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    text = models.TextField('текст', help_text='введите текст комментария')

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self) -> str:
        return truncate(self.text, TRUNCATION)


class Follow(models.Model):
    """Модель ORM для подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='подписчик',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='following',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
