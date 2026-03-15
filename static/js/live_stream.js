(() => {
    const configEl = document.getElementById('liveChatConfig');
    if (!configEl) return;

    const streamId = configEl.dataset.streamId;
    const streamStatus = configEl.dataset.streamStatus;
    const chatMessagesEl = document.getElementById('chatMessages');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatError = document.getElementById('chatError');
    const viewerCount = document.getElementById('viewerCount');
    const videoStatus = document.getElementById('videoStatus');
    const agoraEnabled = configEl.dataset.agoraEnabled === '1';

    if (streamStatus !== 'live') {
        return;
    }

    // ---- Chat WebSocket (always when stream is live) ----
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socketUrl = `${protocol}://${window.location.host}/ws/live-streams/${streamId}/`;

    let socket = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;

    const appendMessage = (payload) => {
        const wrapper = document.createElement('div');
        wrapper.classList.add('mb-2');

        const author = document.createElement('strong');
        author.textContent = payload.username + (payload.user_type === 'cook' ? ' (Cook)' : '');

        const message = document.createElement('span');
        message.textContent = `: ${payload.message}`;

        wrapper.appendChild(author);
        wrapper.appendChild(message);
        chatMessagesEl.appendChild(wrapper);
        chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
    };

    function connectChat() {
        if (socket && socket.readyState === WebSocket.OPEN) return;
        socket = new WebSocket(socketUrl);

        socket.onopen = () => {
            if (chatError) chatError.textContent = '';
            reconnectAttempts = 0;
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'chat_message') {
                appendMessage(data);
                if (chatError) chatError.textContent = '';
            } else if (data.type === 'viewer_count') {
                if (viewerCount) viewerCount.textContent = data.count;
            } else if (data.type === 'error') {
                if (chatError) chatError.textContent = data.message;
            }
        };

        socket.onerror = () => {
            if (chatError) chatError.textContent = 'Connection error. Please try again.';
        };

        socket.onclose = (event) => {
            var msg = 'Connection closed. Refresh the page to reconnect.';
            if (event.reason && event.reason.length) msg = event.reason;
            if (event.code === 4001) msg = 'Please log in again, then refresh the page.';
            if (chatError) chatError.textContent = msg;
            if (reconnectAttempts < maxReconnectAttempts && event.code !== 4001 && event.code !== 4002) {
                reconnectAttempts++;
                setTimeout(connectChat, 2000);
            }
        };
    }

    connectChat();

    chatForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            if (chatError) chatError.textContent = 'Connection lost. Please refresh the page and try again.';
            return;
        }
        try {
            socket.send(JSON.stringify({ message }));
            chatInput.value = '';
        } catch (e) {
            if (chatError) chatError.textContent = 'Connection lost. Please refresh the page and try again.';
        }
    });

    // ---- Agora video (only when credentials present) ----
    if (agoraEnabled) {
        function tryInitAgora() {
            if (window.AgoraRTC) {
                if (videoStatus) videoStatus.textContent = 'Connecting to stream...';
                initializeAgora();
            } else {
                if (videoStatus) videoStatus.textContent = 'Loading video player...';
                setTimeout(tryInitAgora, 100);
            }
        }
        tryInitAgora();
    } else if (videoStatus) {
        videoStatus.textContent = 'Video not configured for this stream.';
    }

    // Agora initialization
    async function initializeAgora() {
        let agoraData;
        try {
            const response = await fetch(`/api/live/${streamId}/agora-token/`, { credentials: 'same-origin' });
            if (!response.ok) {
                throw new Error('Unable to get video token');
            }
            agoraData = await response.json();
        } catch (err) {
            console.error('[Agora] Failed to fetch token:', err);
            if (videoStatus) {
                videoStatus.textContent = 'Failed to fetch video credentials.';
            }
            return;
        }

        const agoraToken = agoraData.token;
        const agoraChannel = agoraData.channel;
        const parsedUid = Number.parseInt(agoraData.uid, 10);
        const agoraUid = Number.isNaN(parsedUid) ? null : parsedUid;
        const agoraAppId = agoraData.app_id;
        if (!agoraToken || !agoraChannel || !agoraAppId || agoraUid == null) {
            if (videoStatus) {
                videoStatus.textContent = 'Video not configured for this stream.';
            }
            return;
        }

        const client = AgoraRTC.createClient({ mode: 'live', codec: 'h264' });

        // Debug: log connection state changes
        client.on('connection-state-change', (curState, prevState) => {
            console.log('[Agora] connection-state-change:', prevState, '→', curState);
            if (videoStatus) {
                videoStatus.textContent = `Agora state: ${curState}`;
            }
        });

        const remoteContainer = document.getElementById('local-player');
        if (!remoteContainer) return;

        const remoteVideoTrack = null;

        client.on('user-published', async (user, mediaType) => {
            await client.subscribe(user, mediaType);

            if (mediaType === 'video') {
                const remoteVideoTrack = user.videoTrack;
                remoteVideoTrack.play(remoteContainer);
                if (videoStatus) {
                    videoStatus.textContent = 'Live video connected.';
                }
            }
            if (mediaType === 'audio') {
                user.audioTrack.play();
            }
        });

        client.on('user-unpublished', (user) => {
            remoteContainer.innerHTML = '';
            if (videoStatus) {
                videoStatus.textContent = 'Broadcaster stopped video.';
            }
        });

        client.on('user-joined', (user) => {
            if (videoStatus) {
                videoStatus.textContent = 'Broadcaster joined. Waiting for video...';
            }
        });

        client.on('user-left', (user) => {
            if (videoStatus) {
                videoStatus.textContent = 'Broadcaster left.';
            }
        });

        client.setClientRole('audience')
            .then(() => client.join(agoraAppId, agoraChannel, agoraToken, agoraUid))
            .then(() => {
                console.log('[Agora] Joined channel:', agoraChannel);
                if (videoStatus) {
                    videoStatus.textContent = `Connected to ${agoraChannel}. Waiting for broadcaster...`;
                }
            })
            .catch((err) => {
                console.error('[Agora] Failed to join channel:', err);
                chatError.textContent = 'Failed to connect to video stream';
                if (videoStatus) {
                    videoStatus.textContent = 'Failed to connect to Agora (check firewall/proxy).';
                }
            });
    }
})();
