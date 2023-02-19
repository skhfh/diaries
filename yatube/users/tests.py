from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'users:signup': 'users/signup.html',
            'users:login': 'users/login.html',
            'users:logout': 'users/logged_out.html',
            'users:password_change_form': 'users/password_change_form.html',
            'users:password_change_done': 'users/password_change_done.html',
            'users:password_reset_form': 'users/password_reset_form.html',
            'users:password_reset_done': 'users/password_reset_done.html',
            'users:password_reset_complete':
                'users/password_reset_complete.html',
        }
        for url_name, template in templates_pages_names.items():
            with self.subTest(url_name=url_name):
                self.setUp()
                response = self.authorized_client.get(reverse(url_name))
                self.assertTemplateUsed(response, template)

    def test_password_reset_confirm_pages_uses_correct_template(self):
        response = self.authorized_client.get(
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': 'uidb64', 'token': 'token'}
            )
        )
        self.assertTemplateUsed(response, 'users/password_reset_confirm.html')

    def test_signup_page_show_correct_context(self):
        """Шаблон signup сформированы с правильным контекстом"""
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        response = self.client.get(reverse('users:signup'))
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class UserCreateFormTests(TestCase):
    def test_create_post(self):
        """Валидная форма создает новго пользователя в User."""
        users_count = User.objects.count()
        print(users_count)
        form_data = {
            'username': 'Test_username',
            'password1': '12345POsE',
            'password2': '12345POsE',
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(username=form_data['username']).exists()
        )
