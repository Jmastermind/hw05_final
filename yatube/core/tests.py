from http import HTTPStatus

from django.test import TestCase

from core.utils import truncate
from yatube.settings import TRUNCATION


class UtilsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.short_text = 'Короткий текст'
        cls.long_text = 'X' * 50

    def test_truncate_long_text(self):
        """Проверяем работу функции truncate c длинным текстом."""
        self.assertEqual(
            truncate(self.long_text, TRUNCATION),
            self.long_text[:TRUNCATION] + '...',
            'Функция truncate работает некорректно с длинным текстом',
        )

    def test_truncate_short_text(self):
        """Проверяем работу функции truncate c коротким текстом."""
        self.assertEqual(
            truncate(self.short_text, TRUNCATION),
            self.short_text[:TRUNCATION],
            'Функция truncate работает некорректно c коротким текстом',
        )


class CoreViewTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.urls = {
            'nonexist': '/nonexist-page/',
        }

    def test_page_status_code(self):
        """Проверяем статусы адресов страниц."""
        httpstatuses = (
            (
                self.urls.get('nonexist'),
                HTTPStatus.NOT_FOUND,
                'Ошибка адреса страницы 404',
            ),
        )
        for url, status, message in httpstatuses:
            with self.subTest(url=url):
                self.assertEqual(
                    self.client.get(url).reason_phrase,
                    status.phrase,
                    message,
                )

    def test_page_template(self):
        """Проверяем, что страница использует соответствующий шаблон."""
        templates = (
            (
                self.urls.get('nonexist'),
                'core/404.html',
                'Ошибка шаблона страницы 404',
            ),
        )
        for url, template, message in templates:
            with self.subTest(url=url, template=template):
                self.assertTemplateUsed(
                    self.client.get(url),
                    template,
                    message,
                )
