
(async () => {
    const config = document.getElementById('local-preview');
    if (!config) return;

    const startBtn = document.getElementById('startPublish');
    const stopBtn = document.getElementById('stopPublish');
    const statusEl = document.getElementById('publishStatus');
    const streamIdInput = document.getElementById('activeStreamId');
    const streamId = streamIdInput ? streamIdInput.value : null;
    const previewEl = document.getElementById('local-preview');

    let client = null;
    let localTracks = [];

    function setStatus(text) {
        if (statusEl) statusEl.textContent = text;
    }

    async function fetchAgoraToken(id) {
        const resp = await fetch(`/api/live/${id}/agora-token/?role=publisher`, { credentials: 'same-origin' });
        if (!resp.ok) throw new Error('Unable to get token');
        return resp.json();
    }

    startBtn.addEventListener('click', async () => {
        startBtn.disabled = true;
        setStatus('Initializing...');

        try {
            if (!streamId) throw new Error('No stream ID');
            const data = await fetchAgoraToken(streamId);
            const appId = data.app_id;
            const token = data.token;
            const channel = data.channel;
            const uid = data.uid;

            client = AgoraRTC.createClient({ mode: 'live', codec: 'h264' });
            await client.setClientRole('host');

            await client.join(appId, channel, token, uid);
            setStatus(`Joined channel: ${channel}`);

            localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();

            // play local video to preview
            localTracks[1].play(previewEl);

            await client.publish(localTracks);

            setStatus('Publishing live');
        } catch (err) {
            console.error('Publish error', err);
            setStatus('Publish failed: ' + (err.message || err));
            startBtn.disabled = false;
        }
    });

    stopBtn.addEventListener('click', async () => {
        stopBtn.disabled = true;
        try {
            if (client && localTracks.length) {
                await client.unpublish(localTracks);
                localTracks.forEach(t => t.close && t.close());
                localTracks = [];
            }
            if (previewEl) previewEl.innerHTML = '';
            setStatus('Not publishing');
            startBtn.disabled = false;
            stopBtn.disabled = false;
        } catch (err) {
            console.error('Stop publish error', err);
            setStatus('Error stopping');
            stopBtn.disabled = false;
        }
    });
})();
