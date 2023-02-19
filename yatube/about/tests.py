from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов /about/author/ и /about/tech/"""
        url_list = [
            '/about/author/',
            '/about/tech/',
        ]
        for url in url_list:
            with self.subTest(address=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_use_correct_template(self):
        """Проверка шаблона для адресов /about/author/ и /about/tech/"""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)


class AboutPagesTest(TestCase):
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for url_name, template in templates_pages_names.items():
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertTemplateUsed(response, template)
