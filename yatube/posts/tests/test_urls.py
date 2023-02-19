from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_url_exists_at_desired_location(self):
        """
        Страницы доступны любому пользователю:
        /, /group/<slug>/, /profile/<username>/, /posts/<post_id>/
        """
        url_list = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.id}/',
        ]
        for url in url_list:
            with self.subTest(address=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_authorized(self):
        """
        Страницы доступны авторизованному пользователю:
        /create/, /follow/
        """
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_only_author(self):
        """
        Страницы доступны только автору:
        /posts/<post_id>/edit/
        """
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_unexisting_page(self):
        """Проверка запроса к несуществующей странице"""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_redirect_anonymous_on_auth_login(self):
        """Страницы перенаправят анонимного пользователя на страницу логина:
        /create/, /follow/
        """
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')
        response = self.client.get('/follow/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/follow/')

    def test_url_redirect_all_except_author_on_post(self):
        """Страницы перенаправят всех пользователей кроме автора
        на страницу поста:
        /posts/<post_id>/edit/
        """
        self.user_2 = User.objects.create_user(username='Not_author')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        response = self.authorized_client_2.get(f'/posts/{self.post.id}/edit/',
                                                follow=True)
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
