import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from faker import Faker
from mixer.backend.django import mixer
from testdata import wrap_testdata

from posts.models import Comment, Group, Post, User
from posts.tests.common import get_image

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    @wrap_testdata
    def setUpTestData(cls):
        cls.group = mixer.blend(Group)
        cls.user = mixer.blend(User)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth = Client()
        cls.auth.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self) -> None:
        """Валидная форма создает новый пост."""
        data = {
            'text': Faker().text(),
            'group': self.group.pk,
            'image': get_image('image_1.gif'),
        }
        self.auth.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        self.assertEqual(
            Post.objects.all().count(),
            1,
            'Неверное количество постов'
            'после отправки валидной формы',
        )
        post = Post.objects.get()
        fields = (
            (
                post.group.pk,
                self.group.pk,
                'У созданного поста неправильная группа',
            ),
            (
                post.text,
                data['text'],
                'У созданного поста неправильный текст',
            ),
            (
                post.image.size,
                data['image'].size,
                'У созданного поста неправильное изображение',
            ),
        )
        for field, expected, message in fields:
            with self.subTest(field=field, expected=expected):
                self.assertEqual(
                    field,
                    expected,
                    message,
                )

    def test_edit_post(self) -> None:
        """Валидная форма сохраняет изменения в посте."""
        post = mixer.blend(Post, group=self.group, author=self.user)
        data = {
            'text': Faker().text(),
            'group': '',
            'image': get_image('image_2.gif'),
        }
        self.auth.post(
            reverse('posts:post_edit', args=(post.pk,)),
            data=data,
            follow=True,
        )
        get_post = Post.objects.get()
        fields = (
            (
                get_post.group,
                None,
                'У измененного поста неправильная группа',
            ),
            (
                get_post.text,
                data['text'],
                'У измененного поста неправильный текст',
            ),
            (
                get_post.image.size,
                data['image'].size,
                'У измененного поста неправильная картинка',
            ),
        )
        for field, expected, message in fields:
            with self.subTest(field=field, expected=expected):
                self.assertEqual(
                    field,
                    expected,
                    message,
                )

    def test_guest_cant_create_post(self) -> None:
        """Аноним не создаёт пост."""
        self.client.post(
            reverse('posts:post_create'),
            data={'text': Faker().text()},
            follow=True,
        )
        self.assertEqual(
            Post.objects.count(),
            0,
            'Неверное количество постов'
            'после создания поста анонимом',
        )

    def test_guest_cant_edit_post(self) -> None:
        """Аноним не редактирует пост."""
        post = mixer.blend(Post, author=self.user)
        data = {
            'text': Faker().text(),
            'group': '',
            'image': get_image('image.gif'),
        }
        self.client.post(
            reverse('posts:post_edit', args=(post.pk,)),
            data=data,
            follow=True,
        )
        get_post = Post.objects.get()
        fields = (
            (
                get_post.group,
                post.group,
                'У измененного поста неправильная группа',
            ),
            (
                get_post.text,
                post.text,
                'У измененного поста неправильный текст',
            ),
            (
                get_post.image,
                post.image,
                'У измененного поста неправильная картинка',
            ),
        )
        for field, expected, message in fields:
            with self.subTest(field=field, expected=expected):
                self.assertEqual(
                    field,
                    expected,
                    message,
                )

    def test_not_author_edit_post(self) -> None:
        """Не автор не редактирует пост."""
        user, auth = mixer.blend(User), Client()
        auth.force_login(user)
        post = mixer.blend(Post, author=self.user, image=None)
        auth.post(
            reverse('posts:post_edit', args=(post.pk,)),
            data={'text': 'Изменение не автором'},
            follow=True,
        )
        self.assertEqual(
            Post.objects.get().text,
            post.text,
            'Текст поста был изменен не автором',
        )


class CommentFormTests(TestCase):
    @classmethod
    @wrap_testdata
    def setUpTestData(cls):
        cls.user, cls.auth = mixer.blend(User), Client()
        cls.auth.force_login(cls.user)
        cls.post = mixer.blend(Post, author=cls.user, image=None)
        cls.post_text = Faker().text()

    def test_create_comment(self) -> None:
        """Валидная форма создает новый коммент."""
        response = self.auth.post(
            reverse('posts:add_comment', args=(self.post.pk,)),
            data={'text': self.post_text},
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post.pk,)),
        )
        comments_count = len(response.context['comments'])
        self.assertEqual(
            comments_count,
            1,
            f'Неверное количество комментов ({comments_count}) '
            'после отправки валидной формы',
        )
        self.assertEqual(
            response.context['comments'][0].text,
            self.post_text,
            'У коммента неправильный текст',
        )

    def test_guest_comment(self) -> None:
        """Аноним не комментит."""
        self.client.post(
            reverse('posts:add_comment', args=(self.post.pk,)),
            data={'text': self.post_text},
            follow=True,
        )
        self.assertEqual(
            Comment.objects.count(),
            0,
            f'Неверное количество комментов ({Comment.objects.count()}) '
            'от анонима',
        )


class FollowTests(TestCase):
    @classmethod
    @wrap_testdata
    def setUpTestData(cls):
        cls.author = mixer.blend(User)
        cls.follower = mixer.blend(User)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower_client = Client()
        cls.follower_client.force_login(cls.follower)

    def test_follow(self) -> None:
        """Успешная подписка на автора."""
        self.follower_client.get(
            reverse('posts:profile_follow', args=(self.author.username,)),
        )
        self.assertTrue(
            self.follower.follower.filter(author=self.author).exists(),
            'Пользователь не может подписаться на автора',
        )
        self.assertEqual(
            self.author.following.all().count(),
            1,
            'Число подписчиков у автора не увеличилось',
        )

    def test_cant_follow_again(self) -> None:
        """Повторная подписка на автора."""
        self.follower_client.get(
            reverse('posts:profile_follow', args=(self.author.username,)),
        )
        self.assertEqual(
            self.follower.follower.filter(author=self.author).count(),
            1,
            'Пользователь может повторно подписаться',
        )

    def test_ufollow(self) -> None:
        """Отписка от автора."""
        self.follower_client.get(
            reverse('posts:profile_unfollow', args=(self.author.username,)),
        )
        self.assertFalse(
            self.follower.follower.filter(author=self.author).exists(),
            'Пользователь не может отписаться от автора',
        )

    def test_self_follow(self) -> None:
        """Самоподписка."""
        self.follower_client.get(
            reverse('posts:profile_unfollow', args=(self.follower.username,)),
        )
        self.assertFalse(
            self.follower.follower.filter(author=self.follower).exists(),
            'Пользователь может подписаться на себя',
        )

    def test_guest_follow(self) -> None:
        """Подписка анонимом."""
        self.client.get(
            reverse('posts:profile_follow', args=(self.author.username,)),
        )
        self.assertEqual(
            self.author.following.all().count(),
            0,
            'Аноним может подписаться',
        )

    def test_follow_guest(self) -> None:
        """Подписка на анонима."""
        self.client.get(
            reverse('posts:profile_follow', args=('guest',)),
        )
        self.assertFalse(
            self.follower.follower.filter(author__username='guest').exists(),
            'Пользователь может подписаться на анонима',
        )
