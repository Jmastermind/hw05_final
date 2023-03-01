from django import forms
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from testdata import wrap_testdata

from posts.models import Follow, Group, Post, User


class YatubePagesTests(TestCase):
    @classmethod
    @wrap_testdata
    def setUpTestData(cls):
        cls.user, cls.auth = mixer.blend(User), Client()
        cls.auth.force_login(cls.user)
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(
            Post,
            author=cls.user,
            group=cls.group,
            image=None,
        )
        cls.urls = {
            'create': reverse('posts:post_create'),
            'detail': reverse('posts:post_detail', args=(cls.post.pk,)),
            'edit': reverse('posts:post_edit', args=(cls.post.pk,)),
            'group': reverse('posts:group_list', args=(cls.group.slug,)),
            'index': reverse('posts:index'),
            'login': reverse('users:login'),
            'profile': reverse(
                'posts:profile',
                args=(cls.user.username,),
            ),
        }

    def test_home_page_context(self) -> None:
        """Проверяем, что шаблон главной страницы с правильным контекстом."""
        contexts = (
            (
                self.auth.get(self.urls['index'])
                .context['page_obj']
                .__len__(),
                1,
                'Неверное количество объектов на главной странице',
            ),
            (
                self.auth.get(self.urls['index'])
                .context['page_obj'][0]
                .author,
                self.post.author,
                'Неверный автор поста',
            ),
            (
                self.auth.get(self.urls['index']).context['page_obj'][0].group,
                self.post.group,
                'Неверная группа поста',
            ),
            (
                self.auth.get(self.urls['index']).context['page_obj'][0].text,
                self.post.text,
                'Неверное содержание текста поста',
            ),
        )
        for context, expected, message in contexts:
            with self.subTest(context=context):
                self.assertEqual(
                    context,
                    expected,
                    message,
                )

    def test_group_page_context(self) -> None:
        """Проверяем, что шаблон страницы группы с правильным контекстом."""
        contexts = (
            (
                self.auth.get(self.urls['group'])
                .context['page_obj']
                .__len__(),
                1,
                'Неверное количество объектов на странице группы',
            ),
            (
                self.auth.get(self.urls['group']).context['group'].description,
                self.group.description,
                'Неверное описание группы',
            ),
            (
                self.auth.get(self.urls['group']).context['group'].slug,
                self.group.slug,
                'Неверный slug группы',
            ),
            (
                self.auth.get(self.urls['group']).context['page_obj'][0].group,
                self.post.group,
                'Неверная группа у поста группы',
            ),
            (
                self.auth.get(self.urls['group']).context['page_obj'][0].text,
                self.post.text,
                'Неверное содержание текста поста группы',
            ),
        )
        for context, expected, message in contexts:
            with self.subTest(context=context):
                self.assertEqual(
                    context,
                    expected,
                    message,
                )

    def test_profile_page_context(self) -> None:
        """Проверяем, что шаблон страницы автора с правильным контекстом."""
        contexts = (
            (
                self.auth.get(self.urls['profile'])
                .context['page_obj']
                .__len__(),
                1,
                'Неверное количество объектов на странице автора',
            ),
            (
                self.auth.get(self.urls['profile'])
                .context['page_obj'][0]
                .author,
                self.post.author,
                'Неверное автор поста на странице автора',
            ),
            (
                self.auth.get(self.urls['profile'])
                .context['page_obj'][0]
                .text,
                self.post.text,
                'Неверное содержание текста поста на странице автора',
            ),
        )
        for context, expected, message in contexts:
            with self.subTest(context=context):
                self.assertEqual(
                    context,
                    expected,
                    message,
                )

    def test_post_page_context(self) -> None:
        """Проверяем, что шаблон страницы поста с правильным контекстом."""
        contexts = (
            (
                self.auth.get(self.urls['detail']).context['post'].author,
                self.post.author,
                'Неверное автор поста на странице поста',
            ),
            (
                self.auth.get(self.urls['detail']).context['post'].text,
                self.post.text,
                'Неверное содержание текста поста на странице поста',
            ),
        )
        for context, expected, message in contexts:
            with self.subTest(context=context):
                self.assertEqual(
                    context,
                    expected,
                    message,
                )

    def test_create_edit_post_page_context(self) -> None:
        """Проверяем, что шаблон post_create/edit с правильным контекстом."""
        fields = (
            (
                'text',
                forms.fields.CharField,
                'Неверный тип поля для текста поста',
            ),
            (
                'group',
                forms.fields.ChoiceField,
                'Неверный тип поля для текста поста',
            ),
        )
        for field, field_type, message in fields:
            with self.subTest(field=field):
                self.assertIsInstance(
                    self.auth.get(self.urls['create'])
                    .context['form']
                    .fields[field],
                    field_type,
                    message,
                )


class PaginatorViewsTest(TestCase):
    @classmethod
    @wrap_testdata
    def setUpTestData(cls):
        cls.user, cls.auth = mixer.blend(User), Client()
        cls.auth.force_login(cls.user)
        cls.group = mixer.blend(Group)
        cls.posts = mixer.cycle(15).blend(
            Post,
            author=cls.user,
            group=cls.group,
            image=None,
        )
        cls.urls = {
            'group': reverse('posts:group_list', args=(cls.group.slug,)),
            'index': reverse('posts:index'),
            'profile': reverse('posts:profile', args=(cls.user.username,)),
        }

    def test_paginator(self) -> None:
        """Проверяем, количество постов на странице."""
        self.client.get(reverse('posts:profile', args=(self.user.username,)))
        pages = (
            (
                self.urls.get('index'),
                settings.PAGINATION,
                'Неверное количество постов на первой странице home',
            ),
            (
                self.urls.get('index') + '?page=2',
                5,
                'Неверное количество постов на второй странице home',
            ),
            (
                self.urls.get('group'),
                settings.PAGINATION,
                'Неверное количество постов на первой странице home',
            ),
            (
                self.urls.get('group') + '?page=2',
                5,
                'Неверное количество постов на второй странице home',
            ),
            (
                self.urls.get('profile'),
                settings.PAGINATION,
                'Неверное количество постов на первой странице home',
            ),
            (
                self.urls.get('profile') + '?page=2',
                5,
                'Неверное количество постов на второй странице home',
            ),
        )
        for page, expected, message in pages:
            with self.subTest(page=page, expected=expected):
                self.assertEqual(
                    self.auth.get(page).context['page_obj'].__len__(),
                    expected,
                    message,
                )


class CacheTest(TestCase):
    def test_home_cache(self) -> None:
        post = mixer.blend(Post, text='Изначальный текст', image=None)
        self.assertEqual(
            self.client.get(reverse('posts:index'))
            .context['page_obj'][0]
            .text,
            post.text,
            'Неверный текст поста до кэширования',
        )
        post.text = 'Текст изменен'
        self.assertEqual(
            self.client.get(reverse('posts:index'))
            .context['page_obj'][0]
            .text,
            'Изначальный текст',
            'Неверный текст поста после кэширования',
        )


class FollowViewTest(TestCase):
    @classmethod
    @wrap_testdata
    def setUpTestData(cls):
        cls.author, cls.follower = mixer.cycle(2).blend(
            User,
            username=(name for name in ('author', 'follower')),
        )
        cls.author_client = Client()
        cls.follower_client = Client()
        cls.author_client.force_login(cls.author)
        cls.follower_client.force_login(cls.follower)
        cls.post = mixer.blend(Post, author=cls.author, image=None)

    def test_follow_profile(self) -> None:
        """Проверяем, что авторизованный пользователь может подписываться."""
        self.follower_client.get(
            reverse('posts:profile_follow', args=(self.author.username,)),
        )
        self.assertTrue(
            self.follower.follower.filter(author=self.author).exists(),
            'Авторизованный пользователь не может подписаться на автора',
        )

    def test_unfollow_profile(self) -> None:
        """Проверяем, что подписчик может отписаться от автора."""
        Follow.objects.create(user=self.follower, author=self.author)
        self.follower_client.get(
            reverse('posts:profile_unfollow', args=(self.author.username,)),
        )
        self.assertFalse(
            self.follower.follower.filter(author=self.author).exists(),
            'Авторизованный пользователь не может отподписаться от автора',
        )

    def test_following_feed(self) -> None:
        """Проверяем, что в ленте подписок есть пост автора."""
        Follow.objects.create(user=self.follower, author=self.author)
        self.assertEqual(
            self.follower_client.get(reverse('posts:follow_index'))
            .context['page_obj']
            .__len__(),
            1,
            'Пост автора отсуствует в ленте подписок',
        )

    def test_not_following_feed(self) -> None:
        """Проверяем, что в ленте подписок нет поста автора, на которого
        не подписан.
        """
        self.assertEqual(
            self.follower_client.get(reverse('posts:follow_index'))
            .context['page_obj']
            .__len__(),
            0,
            'Пост автора, на которого не подписан пользователь есть '
            'в ленте подписок',
        )
