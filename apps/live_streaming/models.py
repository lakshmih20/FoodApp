from django.conf import settings
from django.db import models
from django.utils import timezone
from apps.accounts.models import CookProfile


class LiveStream(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('ended', 'Ended'),
    ]

    cook = models.ForeignKey(CookProfile, on_delete=models.CASCADE, related_name='live_streams')
    order = models.ForeignKey('buyers.BuyerOrder', on_delete=models.SET_NULL, null=True, blank=True, related_name='live_streams', help_text='Order this stream is for (if any)')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='scheduled')
    playback_url = models.URLField(help_text='Public HLS playback URL (AWS IVS) or equivalent.')
    ingest_url = models.URLField(blank=True, help_text='Private ingest URL for encoder (OBS).')
    stream_key = models.CharField(max_length=255, blank=True, help_text='Keep secret. Do not share with viewers.')
    channel_arn = models.CharField(max_length=255, blank=True, help_text='AWS IVS channel ARN (if used).')
    stream_key_arn = models.CharField(max_length=255, blank=True, help_text='AWS IVS stream key ARN (if used).')
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    current_viewers = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.cook.user.username})"

    def start(self):
        self.status = 'live'
        self.started_at = timezone.now()
        self.ended_at = None
        self.save(update_fields=['status', 'started_at', 'ended_at'])

    def end(self):
        self.status = 'ended'
        self.ended_at = timezone.now()
        self.save(update_fields=['status', 'ended_at'])


class LiveChatMessage(models.Model):
    stream = models.ForeignKey(LiveStream, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message[:30]}"


class LiveStreamMute(models.Model):
    stream = models.ForeignKey(LiveStream, on_delete=models.CASCADE, related_name='mutes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('stream', 'user')

    def __str__(self):
        return f"{self.user.username} muted in {self.stream.id}"
