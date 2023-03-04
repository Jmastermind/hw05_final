from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from core.models import AuthoredModel, DefaultModel
from core.utils import truncate

User = get_user_model()


class Group(DefaultModel):
    """Модель ORM для хранения групп постов пользователей."""

    title = models.CharField('название', max_length=200)
    slug = models.SlugField('слаг', max_length=200, unique=True)
    description = models.TextField('описание')

    class Meta:
        verbose_name = 'группа постов'
        verbose_name_plural = 'группы постов'

    def __str__(self) -> str:
        return truncate(self.title, settings.TRUNCATION)


class Post(AuthoredModel):
    """Модель ORM для хранения постов пользователей."""

    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='группа постов',
    )
    image = models.ImageField(
        'картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta(AuthoredModel.Meta):
        default_related_name = 'posts'
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class Comment(AuthoredModel):
    """Модель ORM для хранения комментариев пользователей."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='пост',
    )

    class Meta(AuthoredModel.Meta):
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'


class Follow(DefaultModel):
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

    def __str__(self) -> str:
        return f'Пользователь `{self.user}` подписан на автора `{self.author}`'
