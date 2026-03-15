import time
from django.conf import settings
from agora_token_builder import RtcTokenBuilder


def get_agora_token(stream_id, user_id, is_publisher=False):
    """Generate Agora RTC tokens using the official builder."""
    app_id = settings.AGORA_APP_ID
    app_certificate = settings.AGORA_APP_CERTIFICATE

    if not app_id or not app_certificate:
        raise ValueError("Agora credentials not configured in .env")

    channel_name = f"cook-stream-{stream_id}"
    uid = user_id
    role = 1 if is_publisher else 2
    expiration_ts = int(time.time()) + 3600

    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, app_certificate, channel_name, uid, role, expiration_ts
    )

    return {
        'token': token,
        'channel': channel_name,
        'uid': uid,
        'app_id': app_id,
    }
