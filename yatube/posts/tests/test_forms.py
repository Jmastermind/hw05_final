import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user, cls.auth = mixer.blend(User), Client()
        cls.auth.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self) -> None:
        """Валидная форма создает новый пост."""
        group = mixer.blend(Group)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        data = {
            'text': 'Тестовый текст',
            'group': group.pk,
            'image': uploaded,
        }
        response = self.auth.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user.username,)),
        )
        posts_count = response.context['page_obj'].__len__()
        self.assertEqual(
            posts_count,
            1,
            f'Неверное количество постов ({posts_count}) '
            'после отправки валидной формы',
        )
        fields = (
            (
                response.context['post'].group.pk,
                group.pk,
                'У созданного поста неправильная группа',
            ),
            (
                response.context['post'].text,
                data['text'],
                'У созданного поста неправильный текст',
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
        group = mixer.blend(Group)
        post = mixer.blend(Post, group=group, author=self.user)
        data = {
            'text': 'Текст изменен',
            'group': '',
        }
        response = self.auth.post(
            reverse('posts:post_edit', args=(post.pk,)),
            data=data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(post.pk,)),
        )
        fields = (
            (
                response.context['post'].group,
                None,
                'У измененного поста неправильная группа',
            ),
            (
                response.context['post'].text,
                data['text'],
                'У измененного поста неправильный текст',
            ),
        )
        for field, expected, message in fields:
            with self.subTest(field=field, expected=expected):
                self.assertEqual(
                    field,
                    expected,
                    message,
                )

    def test_guest_create_post(self) -> None:
        """Аноним не создаёт пост."""
        self.client.post(
            reverse('posts:post_create'),
            data={'text': 'Анонимный текст'},
            follow=True,
        )
        self.assertEqual(
            Post.objects.count(),
            0,
            f'Неверное количество постов ({Post.objects.count()}) '
            'после создания поста анонимом',
        )

    def test_guest_edit_post(self) -> None:
        """Аноним не редактирует пост."""
        post = mixer.blend(Post, author=self.user)
        self.client.post(
            reverse('posts:post_edit', args=(post.pk,)),
            data={'text': 'Анонимное изменение'},
            follow=True,
        )
        self.assertEqual(
            Post.objects.get().text,
            post.text,
            'Текст поста был изменен анонимом',
        )

    def test_not_author_edit_post(self) -> None:
        """Не автор не редактирует пост."""
        user, auth = mixer.blend(User, username='tester_2'), Client()
        auth.force_login(user)
        post = mixer.blend(Post, author=self.user)
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
    def setUpClass(cls):
        super().setUpClass()
        cls.user, cls.auth = mixer.blend(User), Client()
        cls.auth.force_login(cls.user)
        cls.post = mixer.blend(Post, author=cls.user)

    def test_create_comment(self) -> None:
        """Валидная форма создает новый коммент."""
        response = self.auth.post(
            reverse('posts:add_comment', args=(self.post.pk,)),
            data={'text': 'Тестовый коммент'},
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
            'Тестовый коммент',
            'У коммента неправильный текст',
        )

    def test_guest_comment(self) -> None:
        """Аноним не комментит."""
        self.client.post(
            reverse('posts:add_comment', args=(self.post.pk,)),
            data={'text': 'Анонимный текст'},
            follow=True,
        )
        self.assertEqual(
            Comment.objects.count(),
            0,
            f'Неверное количество комментов ({Comment.objects.count()}) '
            'от анонима',
        )
