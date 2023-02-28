from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_static_pages_url(self):
        """Проверяем доступность статичных страниц."""
        url = [
            '/about/author/',
            '/about/tech/',
            reverse('about:author'),
            reverse('about:tech'),
        ]
        for url in url:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.reason_phrase,
                    HTTPStatus.OK.phrase,
                    f'Ошибка адреса "{url}": {response.reason_phrase}',
                )

    def test_static_pages_templates(self):
        """Проверяем, шаблоны статических страниц."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Неверный шаблон "{template}" для адреса "{address}"',
                )

    def test_static_pages_use_correct_templates(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertTemplateUsed(
                    self.guest_client.get(reverse_name),
                    template,
                    f'Ошибка соответствия шаблона {template} '
                    f'адресу {reverse_name}',
                )
