from django.conf import settings
from django.test import TestCase
from mixer.backend.django import mixer

from core.utils import truncate
from posts.models import Comment, Follow, Group, Post


class PostModelTest(TestCase):
    def test_post_model_object_name(self) -> None:
        """Проверяем, что у модели Post корректно работает __str__."""
        post = mixer.blend(Post, image=None)
        self.assertEqual(
            str(post),
            truncate(post.text, settings.TRUNCATION),
            'Неверное поле __str__ объекта поста',
        )

    def test_post_model_help_text(self) -> None:
        """Проверяем help_text модели Post."""
        self.assertEqual(
            'введите ваш текст',
            Post._meta.get_field('text').help_text,
            'Неправильное значение help_text объекта поста.',
        )

    def test_post_model_verbose_name(self) -> None:
        """Проверяем verbose_name модели Post."""
        self.assertEqual(
            Post._meta.verbose_name,
            'пост',
            'Неправильный перевод - verbose_name модели Post',
        )

    def test_post_model_verbose_name_plural(self) -> None:
        """Проверяем verbose_name_plural модели Post."""
        self.assertEqual(
            Post._meta.verbose_name_plural,
            'посты',
            'Неправильный перевод - verbose_name_plural модели Post',
        )

    def test_post_model_fields_verbose_name(self) -> None:
        """Проверяем verbose_name полей модели Post."""
        object_names = (
            (
                'author',
                'автор',
            ),
            (
                'group',
                'группа постов',
            ),
            (
                'created',
                'дата создания',
            ),
            (
                'text',
                'текст',
            ),
        )
        for verbose, expected in object_names:
            with self.subTest(verbose=verbose, expected=expected):
                self.assertEqual(
                    Post._meta.get_field(verbose).verbose_name,
                    expected,
                    f'Неправильный перевод - {verbose}',
                )


class GroupModelTest(TestCase):
    def test_group_model_object_name(self) -> None:
        """Проверяем, что у модели Group корректно работает __str__."""
        group = mixer.blend(Group)
        self.assertEqual(
            str(group),
            truncate(group.title, settings.TRUNCATION),
            'Неверное поле __str__ объекта группы',
        )

    def test_group_model_verbose_name(self) -> None:
        """Проверяем verbose_name модели Group."""
        self.assertEqual(
            Group._meta.verbose_name,
            'группа постов',
            'Неправильный перевод - verbose_name модели Group',
        )

    def test_group_model_verbose_name_plural(self) -> None:
        """Проверяем verbose_name_plural модели Group."""
        self.assertEqual(
            Group._meta.verbose_name_plural,
            'группы постов',
            'Неправильный перевод - verbose_name_plural модели Group',
        )

    def test_group_model_fields_verbose_name(self) -> None:
        """Проверяем, verbose_name полей модели Group."""
        object_names = (
            (
                'title',
                'название',
            ),
            (
                'slug',
                'слаг',
            ),
            (
                'description',
                'описание',
            ),
        )
        for verbose, expected in object_names:
            with self.subTest(verbose=verbose, expected=expected):
                self.assertEqual(
                    Group._meta.get_field(verbose).verbose_name,
                    expected,
                    f'Неправильный перевод - {verbose}',
                )


class CommentModelTest(TestCase):
    def test_comment_model_object_name(self) -> None:
        """Проверяем, что у модели Comment корректно работает __str__."""
        post = mixer.blend(Post, image=None)
        comment = mixer.blend(Comment, post=post)
        self.assertEqual(
            str(comment),
            truncate(comment.text, settings.TRUNCATION),
            'Неверное поле __str__ объекта коммента',
        )

    def test_comment_model_verbose_name(self) -> None:
        """Проверяем verbose_name модели Comment."""
        self.assertEqual(
            Comment._meta.verbose_name,
            'комментарий',
            'Неправильный перевод - verbose_name модели Comment',
        )

    def test_comment_model_verbose_name_plural(self) -> None:
        """Проверяем verbose_name_plural модели Comment."""
        self.assertEqual(
            Comment._meta.verbose_name_plural,
            'комментарии',
            'Неправильный перевод - verbose_name_plural модели Comment',
        )

    def test_comment_model_fields_verbose_name(self) -> None:
        """Проверяем, verbose_name полей модели Comment."""
        object_names = (
            (
                'author',
                'автор',
            ),
            (
                'created',
                'дата создания',
            ),
            (
                'post',
                'пост',
            ),
            (
                'text',
                'текст',
            ),
        )
        for verbose, expected in object_names:
            with self.subTest(verbose=verbose, expected=expected):
                self.assertEqual(
                    Comment._meta.get_field(verbose).verbose_name,
                    expected,
                    f'Неправильный перевод - {verbose}',
                )


class FollowModelTest(TestCase):
    def test_follow_model_object_name(self) -> None:
        """Проверяем, что у модели Follow корректно работает __str__."""
        comment = mixer.blend(Follow)
        self.assertEqual(
            str(comment),
            f'Пользователь `{comment.user}` подписан '
            f'на автора `{comment.author}`',
            'Неверное поле __str__ объекта коммента',
        )

    def test_follow_model_verbose_name(self) -> None:
        """Проверяем verbose_name модели Follow."""
        self.assertEqual(
            Follow._meta.verbose_name,
            'подписка',
            'Неправильный перевод - verbose_name модели Follow',
        )

    def test_follow_model_verbose_name_plural(self) -> None:
        """Проверяем verbose_name_plural модели Follow."""
        self.assertEqual(
            Follow._meta.verbose_name_plural,
            'подписки',
            'Неправильный перевод - verbose_name_plural модели Follow',
        )

    def test_follow_model_fields_verbose_name(self) -> None:
        """Проверяем, verbose_name полей модели Follow."""
        object_names = (
            (
                'author',
                'автор',
            ),
            (
                'user',
                'подписчик',
            ),
        )
        for verbose, expected in object_names:
            with self.subTest(verbose=verbose, expected=expected):
                self.assertEqual(
                    Follow._meta.get_field(verbose).verbose_name,
                    expected,
                    f'Неправильный перевод - {verbose}',
                )
