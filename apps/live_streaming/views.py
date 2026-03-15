from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse, HttpResponse

from apps.accounts.models import CookProfile
from .forms import LiveStreamStartForm
from .models import LiveStream
from .services import create_ivs_channel
from .agora_utils import get_agora_token
from apps.buyers.models import BuyerOrder


def _require_cook(user):
    return user.is_authenticated and user.user_type == 'cook'


@login_required
def get_agora_token_api(request, stream_id):
    """API endpoint to get Agora token for an authenticated stream participant."""
    stream = get_object_or_404(LiveStream, id=stream_id)

    if stream.status != 'live':
        return JsonResponse({'error': 'Stream is not live'}, status=400)

    role = request.GET.get('role', 'audience')

    try:
        is_publisher = False
        user_id = request.user.id

        if role == 'publisher':
            if stream.cook.user != request.user or not _require_cook(request.user):
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            is_publisher = True
        elif request.user == stream.cook.user:
            user_id = 1000000 + stream.id

        agora_data = get_agora_token(
            stream_id=stream.id,
            user_id=user_id,
            is_publisher=is_publisher
        )
        return JsonResponse(agora_data)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def stream_list(request):
    live_streams = LiveStream.objects.filter(status='live')
    return render(request, 'live_streaming/stream_list.html', {'live_streams': live_streams})


@login_required
def stream_detail(request, stream_id):
    stream = get_object_or_404(LiveStream, id=stream_id)
    recent_messages = stream.messages.filter(is_deleted=False).select_related('user')[:50]

    agora_enabled = bool(
        stream.status == 'live'
        and settings.LIVE_STREAM_PROVIDER == 'agora'
        and settings.AGORA_APP_ID
        and settings.AGORA_APP_CERTIFICATE
    )

    if stream.status == 'live' and settings.LIVE_STREAM_PROVIDER == 'agora' and not agora_enabled:
        messages.warning(request, 'Video unavailable: Agora credentials are not configured.')

    return render(
        request,
        'live_streaming/stream_detail.html',
        {
            'stream': stream,
            'recent_messages': recent_messages,
            'agora_enabled': agora_enabled,
        },
    )


@login_required
def cook_stream_manage(request):
    if not _require_cook(request.user):
        messages.error(request, 'Access denied. Cook access required.')
        return redirect('buyers:home')

    cook_profile = get_object_or_404(CookProfile, user=request.user)
    order_id = request.GET.get('order')
    active_stream = None
    if order_id:
        # Show/manage stream for this order
        order = get_object_or_404(BuyerOrder, pk=order_id, cook=cook_profile)
        active_stream = LiveStream.objects.filter(order=order, status='live').first()
    else:
        active_stream = LiveStream.objects.filter(cook=cook_profile, status='live').first()

    if request.method == 'POST':
        if 'stop_stream' in request.POST and active_stream:
            active_stream.end()
            messages.success(request, 'Live stream ended.')
            return redirect('live_streaming:cook_manage')

        form = LiveStreamStartForm(request.POST)
        is_auto = 'auto_generate' in request.POST

        if form.is_valid():
            # For Agora, we don't need manual URLs
            use_agora = settings.LIVE_STREAM_PROVIDER == 'agora'
            
            if not is_auto and not use_agora and not form.cleaned_data.get('playback_url'):
                messages.error(request, 'Playback URL is required when auto-generation is not used.')
                return redirect('live_streaming:cook_manage')

            with transaction.atomic():
                LiveStream.objects.filter(cook=cook_profile, status='live').update(
                    status='ended', ended_at=timezone.now()
                )


                new_stream = form.save(commit=False)
                new_stream.cook = cook_profile
                new_stream.status = 'live'
                new_stream.started_at = timezone.now()
                # Link to order if order_id is present
                if order_id:
                    new_stream.order = order

                if is_auto and settings.LIVE_STREAM_PROVIDER == 'aws_ivs':
                    try:
                        ivs_data = create_ivs_channel(request.user.username)
                    except Exception:
                        messages.error(request, 'Unable to auto-create AWS IVS stream. Check AWS credentials.')
                        return redirect('live_streaming:cook_manage')

                    new_stream.playback_url = ivs_data['playback_url']
                    new_stream.ingest_url = ivs_data['ingest_url']
                    new_stream.stream_key = ivs_data['stream_key']
                    new_stream.channel_arn = ivs_data['channel_arn']
                    new_stream.stream_key_arn = ivs_data['stream_key_arn']

                new_stream.save()
                if settings.LIVE_STREAM_PROVIDER == 'agora':
                    new_stream.playback_url = f"agora://cook-stream-{new_stream.id}"
                    new_stream.save(update_fields=['playback_url'])

            messages.success(request, 'Live stream started. Share the live link with viewers.')
            return redirect('live_streaming:cook_manage')
    else:
        form = LiveStreamStartForm()

    return render(
        request,
        'live_streaming/cook_stream_manage.html',
        {
            'form': form,
            'active_stream': active_stream,
        },
    )


@login_required
def debug_streams(request):
    streams = LiveStream.objects.all().order_by('-started_at')
    rows = [
        f"<tr><td>{s.id}</td><td>{s.status}</td><td>{s.order_id}</td><td>{s.cook.user.username}</td><td>{s.title}</td></tr>"
        for s in streams
    ]
    html = """
    <h2>All LiveStreams</h2>
    <table border='1' cellpadding='5'>
        <tr><th>ID</th><th>Status</th><th>Order ID</th><th>Cook</th><th>Title</th></tr>
        {} 
    </table>
    """.format("\n".join(rows))
    return HttpResponse(html)
