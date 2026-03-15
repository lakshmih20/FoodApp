from django.contrib import admin
from .models import LiveStream, LiveChatMessage, LiveStreamMute


@admin.register(LiveStream)
class LiveStreamAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'cook', 'order', 'status', 'started_at', 'current_viewers')
    list_filter = ('status',)
    search_fields = ('title', 'cook__user__username')


@admin.register(LiveChatMessage)
class LiveChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'stream', 'user', 'created_at', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('user__username', 'message')


@admin.register(LiveStreamMute)
class LiveStreamMuteAdmin(admin.ModelAdmin):
    list_display = ('id', 'stream', 'user', 'created_at')
    search_fields = ('user__username',)
