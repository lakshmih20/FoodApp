from django.urls import path
from . import views

app_name = 'live_streaming'

urlpatterns = [
    path('live/', views.stream_list, name='stream_list'),
    path('live/<int:stream_id>/', views.stream_detail, name='stream_detail'),
    path('live/cook/manage/', views.cook_stream_manage, name='cook_manage'),
    path('api/live/<int:stream_id>/agora-token/', views.get_agora_token_api, name='get_agora_token'),
    path('debug/streams/', views.debug_streams, name='debug_streams'),
]
