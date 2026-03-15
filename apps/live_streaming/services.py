import uuid

import boto3
from django.conf import settings


def create_ivs_channel(cook_username: str):
    """
    Creates an AWS IVS channel + stream key. Returns playback URL, ingest URL, and key.
    Requires AWS credentials in environment variables or IAM role.
    """
    client = boto3.client('ivs', region_name=settings.AWS_REGION)

    channel_name = f"cook-{cook_username}-{uuid.uuid4().hex[:8]}"
    channel_response = client.create_channel(
        name=channel_name,
        type='STANDARD',
        latencyMode='LOW',
        authorized=False,
    )

    channel = channel_response['channel']
    channel_arn = channel['arn']
    playback_url = channel['playbackUrl']
    ingest_endpoint = channel['ingestEndpoint']
    ingest_url = f"rtmps://{ingest_endpoint}:443/app/"

    stream_key_response = client.create_stream_key(channelArn=channel_arn)
    stream_key = stream_key_response['streamKey']['value']
    stream_key_arn = stream_key_response['streamKey']['arn']

    return {
        'playback_url': playback_url,
        'ingest_url': ingest_url,
        'stream_key': stream_key,
        'channel_arn': channel_arn,
        'stream_key_arn': stream_key_arn,
    }
