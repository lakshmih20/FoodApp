import json
from datetime import timedelta
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.db import models
from django.core.cache import cache
from django.utils import timezone

from .models import LiveStream, LiveChatMessage, LiveStreamMute


class LiveStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        raw_id = self.scope['url_route']['kwargs']['stream_id']
        self.stream_id = int(raw_id) if isinstance(raw_id, str) and raw_id.isdigit() else raw_id
        self.user = self.scope['user']
        self.group_name = f"live_stream_{self.stream_id}"

        if not self.user.is_authenticated:
            await self.close(code=4001, reason="Please log in to use chat.")
            return

        stream = await self._get_stream()
        if not stream or stream.status != 'live':
            await self.close(code=4002, reason="Stream not available.")
            return

        muted = await self._is_muted()
        if muted:
            await self.close(code=4003, reason="You are muted.")
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self._increment_viewers()
        await self._broadcast_viewers()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self._decrement_viewers()
        await self._broadcast_viewers()

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            return
        message = (data.get('message') or '').strip()
        if not message:
            return

        if len(message) > settings.LIVE_CHAT_MAX_MESSAGE_LENGTH:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message too long.'
            }))
            return

        if not await self._rate_limit_ok():
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'You are sending messages too quickly.'
            }))
            return

        stream = await self._get_stream()
        if not stream or stream.status != 'live':
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Stream is not live.'
            }))
            return

        muted = await self._is_muted()
        if muted:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'You are muted for this stream.'
            }))
            return

        try:
            chat_message = await self._create_message(message)
        except Exception:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Could not send. Please try again.'
            }))
            return

        payload = {
            'type': 'chat_message',
            'message': chat_message.message,
            'username': self.user.username,
            'user_type': self.user.user_type,
            'created_at': chat_message.created_at.isoformat(),
        }
        try:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'broadcast_message',
                    'payload': payload,
                }
            )
        except Exception:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Could not send. Please try again.'
            }))

    async def broadcast_message(self, event):
        await self.send(text_data=json.dumps(event['payload']))

    async def broadcast_viewer_count(self, event):
        await self.send(text_data=json.dumps({
            'type': 'viewer_count',
            'count': event['count'],
        }))

    async def _broadcast_viewers(self):
        stream = await self._get_stream()
        if not stream:
            return
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'broadcast_viewer_count',
                'count': stream.current_viewers,
            }
        )

    @database_sync_to_async
    def _get_stream(self):
        return LiveStream.objects.filter(id=self.stream_id).first()

    @database_sync_to_async
    def _create_message(self, message):
        return LiveChatMessage.objects.create(
            stream_id=self.stream_id,
            user=self.user,
            message=message,
        )

    @database_sync_to_async
    def _is_muted(self):
        return LiveStreamMute.objects.filter(stream_id=self.stream_id, user=self.user).exists()

    @database_sync_to_async
    def _increment_viewers(self):
        LiveStream.objects.filter(id=self.stream_id).update(
            current_viewers=models.F('current_viewers') + 1
        )

    @database_sync_to_async
    def _decrement_viewers(self):
        LiveStream.objects.filter(id=self.stream_id, current_viewers__gt=0).update(
            current_viewers=models.F('current_viewers') - 1
        )

    async def _rate_limit_ok(self):
        key = f"chat_rate:{self.stream_id}:{self.user.id}"
        now = timezone.now()
        last_sent = cache.get(key)
        if last_sent and now - last_sent < timedelta(seconds=settings.LIVE_CHAT_MIN_SECONDS_BETWEEN_MESSAGES):
            return False
        cache.set(key, now, timeout=settings.LIVE_CHAT_MIN_SECONDS_BETWEEN_MESSAGES)
        return True
