from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user, cls.author_user = mixer.cycle(2).blend(User)
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(Post, author=cls.author_user)
        cls.auth = Client()
        cls.author = Client()
        cls.auth.force_login(cls.user)
        cls.author.force_login(cls.author_user)

        cls.urls = {
            'create': reverse('posts:post_create'),
            'edit': reverse('posts:post_edit', args=(cls.post.pk,)),
            'detail': reverse('posts:post_detail', args=(cls.post.pk,)),
            'group': reverse('posts:group_list', args=(cls.group.slug,)),
            'index': reverse('posts:index'),
            'login': reverse('users:login'),
            'missing': 'missing',
            'profile': reverse(
                'posts:profile',
                args=(cls.author_user.username,),
            ),
        }

    def test_http_statuses(self) -> None:
        """Проверяем доступность адресов страниц."""
        httpstatuses = (
            # Публичные страницы
            (
                self.urls.get('detail'),
                HTTPStatus.OK,
                self.client,
                'Ошибка адреса страницы поста',
            ),
            (
                self.urls.get('group'),
                HTTPStatus.OK,
                self.client,
                'Ошибка адреса группы постов',
            ),
            (
                self.urls.get('index'),
                HTTPStatus.OK,
                self.client,
                'Ошибка адреса главной страницы',
            ),
            (
                self.urls.get('missing'),
                HTTPStatus.NOT_FOUND,
                self.client,
                'Ошибка адреса несуществующей страницы',
            ),
            (
                self.urls.get('profile'),
                HTTPStatus.OK,
                self.client,
                'Ошибка адреса страницы автора',
            ),
            # Приватные страницы
            (
                self.urls.get('create'),
                HTTPStatus.FOUND,
                self.client,
                'Ошибка адреса страницы создания поста (гость)',
            ),
            (
                self.urls.get('create'),
                HTTPStatus.OK,
                self.auth,
                'Ошибка адреса страницы создания поста (пользователь)',
            ),
            (
                self.urls.get('edit'),
                HTTPStatus.FOUND,
                self.auth,
                'Ошибка адреса страницы редактирования поста (не автор)',
            ),
            (
                self.urls.get('edit'),
                HTTPStatus.OK,
                self.author,
                'Ошибка адреса страницы редактирования поста (автор)',
            ),
        )
        for url, status, client, message in httpstatuses:
            with self.subTest(url=url):
                self.assertEqual(
                    client.get(url).reason_phrase,
                    status.phrase,
                    message,
                )

    def test_templates(self) -> None:
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        templates = (
            (
                self.urls.get('detail'),
                'posts/post_detail.html',
                self.client,
                'Страница поста использует неправильный шаблон',
            ),
            (
                self.urls.get('create'),
                'posts/create_post.html',
                self.auth,
                'Страница создания поста использует неправильный шаблон',
            ),
            (
                self.urls.get('edit'),
                'posts/create_post.html',
                self.author,
                'Страница редактирования поста использует неправильный шаблон',
            ),
            (
                self.urls.get('group'),
                'posts/group_list.html',
                self.client,
                'Страница группы использует неправильный шаблон',
            ),
            (
                self.urls.get('index'),
                'posts/index.html',
                self.client,
                'Главная страница использует неправильный шаблон',
            ),
            (
                self.urls.get('profile'),
                'posts/profile.html',
                self.client,
                'Cтраница автора использует неправильный шаблон',
            ),
        )
        for url, template, client, message in templates:
            with self.subTest(url=url, template=template):
                self.assertTemplateUsed(client.get(url), template, message)

    def test_redirects(self) -> None:
        """Проверяем переадресацию при отсуствии прав у пользователя."""
        redirects = (
            (
                self.urls.get('create'),
                redirect_to_login(self.urls.get('create')).url,
                self.client,
            ),
            (
                self.urls.get('edit'),
                redirect_to_login(self.urls.get('edit')).url,
                self.client,
            ),
            (
                self.urls.get('edit'),
                self.urls.get('detail'),
                self.auth,
            ),
        )
        for url_from, url_to, client in redirects:
            with self.subTest(url=url_from):
                self.assertRedirects(client.get(url_from), url_to)
