(() => {
    const configEl = document.getElementById('buyerNotificationConfig');
    if (!configEl) {
        return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socketUrl = `${protocol}://${window.location.host}/ws/notifications/`;
    const toastHost = document.getElementById('buyerNotificationToasts');
    let socket = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;

    const showToast = (message) => {
        if (!toastHost || !message) {
            return;
        }

        const toastEl = document.createElement('div');
        toastEl.className = 'toast align-items-center text-bg-success border-0';
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastHost.appendChild(toastEl);
        const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
        toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
        toast.show();
    };

    const connect = () => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            return;
        }

        socket = new WebSocket(socketUrl);

        socket.onopen = () => {
            reconnectAttempts = 0;
        };

        socket.onmessage = (event) => {
            let data;
            try {
                data = JSON.parse(event.data);
            } catch (error) {
                return;
            }

            if (data.type === 'notification' && data.notification && data.notification.message) {
                showToast(data.notification.message);
                window.dispatchEvent(new CustomEvent('buyer-order-notification', { detail: data.notification }));
            }
        };

        socket.onclose = (event) => {
            if (event.code === 4001) {
                return;
            }

            if (reconnectAttempts < maxReconnectAttempts) {
                reconnectAttempts += 1;
                window.setTimeout(connect, 2000);
            }
        };
    };

    connect();
})();