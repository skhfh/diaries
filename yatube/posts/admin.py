from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    """Добавление в админку управление постами"""
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Добавление в админку управление группами"""
    list_display = ('pk', 'title', 'slug', 'description',)
    search_fields = ('title',)


class CommentAdmin(admin.ModelAdmin):
    """Добавление в админку управление комментариями"""
    list_display = ('pk', 'author', 'post', 'text', 'created',)
    search_fields = ('text',)
    list_filter = ('created',)


class FollowAdmin(admin.ModelAdmin):
    """Добавление в админку управление подписками"""
    list_display = ('pk', 'user', 'author')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
