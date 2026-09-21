from django.contrib import admin
from .models import Category, Channel, Comment, Follow, Like, Profile, Video


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified')
    list_filter = ('is_verified',)


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'created_at')
    search_fields = ('title', 'owner__username')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'channel', 'category', 'views_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video', 'created_at')


admin.site.register(Follow)
admin.site.register(Like)