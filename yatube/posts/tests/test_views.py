from http import HTTPStatus
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

NUMBER_OF_POST_ON_ONE_PAGE: int = 10

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Test text of comment',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def method_checks_post(self, post_object):
        checked_fields = {
            post_object.pk: self.post.pk,
            post_object.author: self.user,
            post_object.text: self.post.text,
            post_object.group: self.group,
            post_object.image: self.post.image,
        }
        for field, expected in checked_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}
                    ): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}
                    ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_group_profile_pages_show_correct_context(self):
        """
        Шаблоны сформированы с правильным контекстом: index, group_list,
        profile
        """
        url_name_list = {
            'posts:index': {},
            'posts:group_list': {'slug': f'{self.group.slug}'},
            'posts:profile': {'username': f'{self.user.username}'},
        }
        for url_name, url_kwargs in url_name_list.items():
            response = self.client.get(
                reverse(url_name, kwargs=url_kwargs)
            )
            first_object = response.context.get('page_obj')[0]
            self.method_checks_post(first_object)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформированы с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.pk}'})
        )
        post_obj_value = response.context['post']
        self.method_checks_post(post_obj_value)
        form_field = response.context['form'].fields.get('text')
        self.assertIsInstance(form_field, forms.fields.CharField)
        comment = response.context['post_comments'][0]
        self.assertEqual(comment, self.comment)

    def test_create_post_page_show_correct_context(self):
        """
        Шаблон create_post (создание) сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """
        Шаблон create_post (редактирование) сформирован с
        правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        expected_is_edit = response.context.get('is_edit')
        self.assertTrue(expected_is_edit)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_created_post_appears_on_the_right_pages(self):
        """
        Новый созданный пост появляется на главной странице,
        страницах его группы и автора, и не появляется не в другой группе
        """
        wrong_group = Group.objects.create(
            title='Wrong group',
            slug='wrong-slug',
            description='some description')
        new_post = Post.objects.create(
            author=self.user,
            text='some text',
            group=self.group
        )
        url_name_list = {
            'posts:index': {},
            'posts:group_list': {'slug': f'{self.group.slug}'},
            'posts:profile': {'username': f'{self.user.username}'},
        }
        for url_name, url_kwargs in url_name_list.items():
            with self.subTest(url_name=url_name):
                response = self.client.get(
                    reverse(url_name, kwargs=url_kwargs)
                )
                post_from_context = response.context.get('page_obj')[0]
                self.assertEqual(post_from_context, new_post)
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': wrong_group.slug})
        )
        page_obj = response.context.get('page_obj')
        self.assertNotIn(new_post, page_obj)

    def test_index_page_cache(self):
        new_post = Post.objects.create(
            author=self.user,
            text='New post text'
        )
        new_post_id = new_post.pk
        response = self.client.get(reverse('posts:index'))
        page_obj = response.context.get('page_obj')
        self.assertIn(new_post, page_obj)
        Post.objects.filter(pk=new_post_id).delete()
        response_post_del = self.client.get(reverse('posts:index'))
        self.assertEqual(response_post_del.content, response.content)
        cache.clear()
        response_cache_del = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response_cache_del.content, response.content)

    def test_follow_and_unfollow(self):
        author = User.objects.create_user(username='Author')
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': author.username})
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': author.username}
        ))
        self.assertTrue(Follow.objects.filter(
            user=self.user,
            author=author
        ).exists()
        )
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': author.username})
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': author.username}
        ))
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=author
        ).exists()
        )

    def test_new_post_only_on_follower_page(self):
        follower = User.objects.create_user(username='Follower')
        follower_client = Client()
        follower_client.force_login(follower)
        not_follower = User.objects.create_user(username='Not follower')
        not_follower_client = Client()
        not_follower_client.force_login(not_follower)
        Follow.objects.create(user=follower, author=self.user)
        new_post = Post.objects.create(
            author=self.user,
            text='New post text'
        )
        response = follower_client.get(reverse('posts:follow_index'))
        page_obj = response.context.get('page_obj')
        self.assertIn(new_post, page_obj)
        response = not_follower_client.get(reverse('posts:follow_index'))
        page_obj = response.context.get('page_obj')
        self.assertFalse(page_obj)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create((
            Post(
                text=f'Тестовый текст {i}',
                author=cls.user,
                group=cls.group
            ) for i in range(NUMBER_OF_POST_ON_ONE_PAGE + 4)
        ))

    def setUp(self):
        cache.clear()

    def test_paginator(self):
        """
        Проверка работы пагинатора и первого поста шаблонов:
        index, group_list, profile.
        """
        url_name_and_queryset = [
            [
                'posts:index',
                {},
                Post.objects.all()
            ],
            [
                'posts:group_list',
                {'slug': f'{self.group.slug}'},
                self.group.posts.all()
            ],
            [
                'posts:profile',
                {'username': f'{self.user.username}'},
                self.user.posts.all()
            ],
        ]
        for url_name, url_kwargs, queryset in url_name_and_queryset:
            with self.subTest(url_name=url_name):
                page_list = [
                    ['', 0, NUMBER_OF_POST_ON_ONE_PAGE],
                    ['?page=2',
                     NUMBER_OF_POST_ON_ONE_PAGE,
                     NUMBER_OF_POST_ON_ONE_PAGE + 4
                     ],
                ]
                for page, post_num_start, post_num_end in page_list:
                    response = self.client.get(
                        reverse(url_name, kwargs=url_kwargs) + page
                    )
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    page_obj = response.context.get('page_obj')
                    self.assertIsNotNone(page_obj)
                    self.assertIsInstance(page_obj, Page)
                    self.assertQuerysetEqual(
                        page_obj.object_list,
                        queryset[post_num_start:post_num_end],
                        transform=lambda x: x
                    )
