from django.test import TestCase
from mixer.backend.django import mixer

from core.utils import truncate
from posts.models import Group, Post
from yatube.settings import TRUNCATION


class PostModelTest(TestCase):
    def test_post_model_object_name(self) -> None:
        """Проверяем, что у модели Post корректно работает __str__."""
        post = mixer.blend(Post)
        self.assertEqual(
            str(post),
            f'Пост {post.pk}: {truncate(post.text, TRUNCATION)}',
            'Неверное поле __str__ объекта поста',
        )

    def test_post_model_help_text(self) -> None:
        """Проверяем help_text модели Post."""
        self.assertEqual(
            'введите текст поста',
            Post._meta.get_field('text').help_text,
            'Неправильное значение help_text объекта поста.',
        )

    def test_post_model_verbose_name(self) -> None:
        """Проверяем verbose_name модели Post"""
        self.assertEqual(
            Post._meta.verbose_name,
            'пост',
            'Неправильный перевод - verbose_name модели Post',
        )

    def test_post_model_verbose_name_plural(self) -> None:
        """Проверяем verbose_name_plural модели Post"""
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
                'author',
            ),
            (
                'group',
                'группа постов',
                'group',
            ),
            (
                'created',
                'Дата создания',
                'created',
            ),
            (
                'text',
                'текст',
                'text',
            ),
        )
        for verbose, expected, target in object_names:
            with self.subTest(verbose=verbose, target=target):
                self.assertEqual(
                    Post._meta.get_field(verbose).verbose_name,
                    expected,
                    f'Неправильный перевод - {target}',
                )


class GroupModelTest(TestCase):
    def test_group_model_object_name(self) -> None:
        """Проверяем, что у модели Group корректно работает __str__."""
        group = mixer.blend(Group)
        self.assertEqual(
            str(group),
            truncate(group.title, TRUNCATION),
            'Неверное поле __str__ объекта группы',
        )

    def test_group_model_verbose_name(self) -> None:
        """Проверяем verbose_name модели Group"""
        self.assertEqual(
            Group._meta.verbose_name,
            'группа постов',
            'Неправильный перевод - verbose_name модели Group',
        )

    def test_group_model_verbose_name_plural(self) -> None:
        """Проверяем verbose_name_plural модели Group"""
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
                'title',
            ),
            (
                'slug',
                'слаг',
                'slug',
            ),
            (
                'description',
                'описание',
                'description',
            ),
        )
        for verbose, expected, target in object_names:
            with self.subTest(verbose=verbose):
                self.assertEqual(
                    Group._meta.get_field(verbose).verbose_name,
                    expected,
                    f'Неправильный перевод - {target}',
                )
