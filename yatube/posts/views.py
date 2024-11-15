from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from yatube.settings import NUMBER_OF_POSTS
from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post
from .utils import paginator

User = get_user_model()


@cache_page(20, key_prefix='index_page')
def index(request):
    """Главная страница с настроенной пагинацией.
    Настроено кэширование страницы
    """
    post_list = Post.objects.select_related('group').all()
    page_obj = paginator(request, post_list, NUMBER_OF_POSTS)
    context = {
        'index': True,
        'follow': False,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница постов в конкретной группе slug с настроенной пагинацией"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(request, post_list, NUMBER_OF_POSTS)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Страница автора с его постами, можно подписаться/отписаться
    (для авторизованных пользователей)
    """
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    page_obj = paginator(request, post_list, NUMBER_OF_POSTS)
    current_user = request.user
    if current_user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
    else:
        following = False
    context = {
        'following': following,
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Страница конкретного поста, с формой для написания комментария
    (для авторизованных пользователей) и уже написанными комментариями
    """
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    post_comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'form': form,
        'post_comments': post_comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Страница создания нового поста (для авторизованных пользователей
    "@login_required")
    """
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Страница редактирования поста (для авторизованного автора этого поста)
    """
    if request.user != get_object_or_404(Post, pk=post_id).author:
        return redirect('posts:post_detail', post_id=post_id)
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html', {
        'form': form,
        'is_edit': is_edit,
    })


@login_required
def add_comment(request, post_id):
    """Обработчик для создания комментария. Форма отображается на странице
    поста
    """
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        post = Post.objects.get(pk=post_id)
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Страница с постами любимых авторов (для авторизованных)"""
    current_user = request.user
    post_list = Post.objects.filter(author__following__user=current_user).all()
    page_obj = paginator(request, post_list, NUMBER_OF_POSTS)
    context = {
        'index': False,
        'follow': True,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписка на автора"""
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора"""
    author = get_object_or_404(User, username=username)
    user = request.user
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', username=username)
