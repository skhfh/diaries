import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test description'
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.last()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.image, 'posts/small.gif')

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый текст',
        )
        post_id = post.pk
        form_data = {
            'text': 'Отредактированный тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': post_id}
        ))
        self.assertTrue(
            Post.objects.filter(
                pk=post_id,
                author=self.user,
                text=form_data['text'],
            ).exists()
        )

    def test_fields_label_and_help_text(self):
        """Проверяем label и help_text форм создания и редактирования поста."""
        label_and_help_text_list = {
            'text': ['Текст поста', 'Текст нового поста'],
            'group': ['Группа', 'Группа, к которой будет относиться пост'],
            'image': ['Картинка', 'Загрузите картинку для вашего поста'],
        }
        for field, label_and_help_text in label_and_help_text_list.items():
            expected_label, expected_help_text = label_and_help_text
            value_label = self.form.fields[field].label
            value_help_text = self.form.fields[field].help_text
            self.assertEqual(value_label, expected_label)
            self.assertEqual(value_help_text, expected_help_text)

    def test_creat_comment(self):
        """Валидная форма создает комментарий у поста."""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый текст',
        )
        post_id = post.pk
        comments_count = Comment.objects.filter(post=post).count()
        form_data = {'text': 'Тестовый текст комментария'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': post_id}
        ))
        self.assertEqual(
            Comment.objects.filter(post=post).count(),
            comments_count + 1
        )
        comment = Comment.objects.filter(post=post).last()
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.text, form_data['text'])

    def test_comment_not_created_by_anonymous(self):
        """
        Анонимный пользователь не может создать комментарий.
        """
        post = Post.objects.create(
            author=self.user,
            text='Тестовый текст',
        )
        post_id = post.pk
        comments_count = Comment.objects.filter(post=post).count()
        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data={'text': 'Comment text'},
            follow=True
        )
        self.assertEqual(
            Comment.objects.filter(post=post).count(),
            comments_count
        )
