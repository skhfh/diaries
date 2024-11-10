from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма для поста (создание/чтение/изменение)"""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }


class CommentForm(forms.ModelForm):
    """Форма для создания комментария"""
    class Meta:
        model = Comment
        fields = ('text',)
