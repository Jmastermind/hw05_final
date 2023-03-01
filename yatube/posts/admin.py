from django.contrib import admin

from posts.models import Comment, Follow, Group, Post
from yatube.admin import BaseAdmin


@admin.register(Post)
class PostAdmin(BaseAdmin):
    list_display = ('pk', 'text', 'created', 'author', 'group')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)


@admin.register(Group)
class GroupAdmin(BaseAdmin):
    list_display = ('title', 'slug')


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = ('author', 'text')
    list_editable = ('text',)
    search_fields = ('text',)
    list_filter = ('created',)


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    list_display = ('author', 'user')
    list_editable = ('user',)
    list_filter = ('author',)
