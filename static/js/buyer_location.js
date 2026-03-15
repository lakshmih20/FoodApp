(function () {
    const chip = document.getElementById('buyer-location-chip');
    const label = document.getElementById('buyer-location-label');
    const modal = document.getElementById('locationModal');
    if (!modal) {
        return;
    }

    const messageEl = document.getElementById('location-modal-message');
    const searchInput = document.getElementById('location-search-input');
    const searchBtn = document.getElementById('location-search-btn');
    const searchResults = document.getElementById('location-search-results');
    const useCurrentBtn = document.getElementById('location-use-current-btn');
    const currentResult = document.getElementById('location-current-result');
    const pincodeInput = document.getElementById('location-pincode-input');
    const pincodeBtn = document.getElementById('location-pincode-btn');
    const recentList = document.getElementById('recent-locations-list');
    const savedList = document.getElementById('saved-addresses-list');
    const closeBtn = document.getElementById('location-modal-close');
    const skipBtn = document.getElementById('location-skip-btn');

    const endpoint = {
        state: '/buyers/api/location/state/',
        current: '/buyers/api/location/set-current/',
        pincode: '/buyers/api/location/set-pincode/',
        search: '/buyers/api/location/search/',
        select: '/buyers/api/location/select/',
        skip: '/buyers/api/location/skip/'
    };

    function getCsrfToken() {
        const m = document.cookie.match(/csrftoken=([^;]+)/);
        return m ? m[1] : '';
    }

    function setMessage(text) {
        if (messageEl) {
            messageEl.textContent = text || '';
        }
    }

    function openModal(forceTitle) {
        const title = document.getElementById('location-modal-title');
        if (title && forceTitle) {
            title.textContent = forceTitle;
        }
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    function closeModal(markDismissed) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        if (markDismissed && label && label.textContent.trim() === 'Set Location') {
            fetch(endpoint.skip, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });
        }
    }

    function locationButtonHtml(item) {
        const distance = item.distance_km != null ? ` <span style="color:#6b7280; font-size:12px;">(${item.distance_km} km)</span>` : '';
        return `<button type="button" class="buyer-location-select" data-lat="${item.lat}" data-lng="${item.lng}" data-name="${(item.location_name || '').replace(/"/g, '&quot;')}" data-pincode="${item.pincode || ''}" style="text-align:left; border:1px solid #e3e7e3; border-radius:10px; padding:8px 10px; background:#fff;">📍 ${item.location_name || 'Unknown'}${distance}</button>`;
    }

    async function fetchState() {
        const res = await fetch(endpoint.state);
        return res.json();
    }

    function renderState(data) {
        if (!data || !data.success) {
            return;
        }
        if (label) {
            label.textContent = (data.current && data.current.location_name) ? data.current.location_name : 'Set Location';
        }

        recentList.innerHTML = '';
        (data.recent_locations || []).forEach((item) => {
            recentList.insertAdjacentHTML('beforeend', locationButtonHtml(item));
        });
        if (!(data.recent_locations || []).length) {
            recentList.innerHTML = '<small style="color:#777;">No recent locations yet.</small>';
        }

        savedList.innerHTML = '';
        (data.saved_addresses || []).forEach((item) => {
            savedList.insertAdjacentHTML('beforeend', locationButtonHtml(item));
        });
        if (!(data.saved_addresses || []).length) {
            savedList.innerHTML = '<small style="color:#777;">No saved addresses.</small>';
        }
    }

    async function selectLocation(payload) {
        const res = await fetch(endpoint.select, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!data.success) {
            setMessage(data.message || 'Unable to update location.');
            return;
        }
        closeModal();
        window.location.reload();
    }

    if (chip) {
        chip.addEventListener('click', async () => {
            setMessage('');
            const data = await fetchState();
            renderState(data);
            openModal('Change your location');
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', () => closeModal(true));
    }

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal(true);
        }
    });

    if (skipBtn) {
        skipBtn.addEventListener('click', async () => {
            await fetch(endpoint.skip, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });
            closeModal();
        });
    }

    if (searchBtn) {
        searchBtn.addEventListener('click', async () => {
            const q = (searchInput.value || '').trim();
            if (q.length < 3) {
                setMessage('Type at least 3 characters to search.');
                return;
            }
            setMessage('');
            const res = await fetch(`${endpoint.search}?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            if (!data.success || !(data.results || []).length) {
                searchResults.innerHTML = '<small style="color:#777;">No matching locations found.</small>';
                return;
            }
            searchResults.innerHTML = data.results
                .map((item) => locationButtonHtml(item))
                .join('');
        });
    }

    if (useCurrentBtn) {
        useCurrentBtn.addEventListener('click', () => {
            setMessage('');
            if (!navigator.geolocation) {
                setMessage('Geolocation is not supported by your browser.');
                return;
            }
            currentResult.textContent = 'Detecting your location...';
            navigator.geolocation.getCurrentPosition(async (pos) => {
                const res = await fetch(endpoint.current, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({ lat: pos.coords.latitude, lng: pos.coords.longitude })
                });
                const data = await res.json();
                if (!data.success) {
                    setMessage(data.message || 'Could not detect location.');
                    currentResult.textContent = '';
                    return;
                }
                if (currentResult) {
                    currentResult.textContent = `📍 ${data.location.location_name} (${data.location.pincode || ''})`;
                }
                setTimeout(() => {
                    closeModal();
                    window.location.reload();
                }, 1200);
            }, () => {
                setMessage('Unable to access your current location. Please allow location access in your browser settings.');
                currentResult.textContent = '';
            }, { timeout: 10000 });
        });
    }

    if (pincodeBtn) {
        pincodeBtn.addEventListener('click', async () => {
            const pincode = (pincodeInput.value || '').trim();
            if (!pincode) {
                setMessage('Please enter a pincode.');
                return;
            }
            const res = await fetch(endpoint.pincode, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ pincode: pincode })
            });
            const data = await res.json();
            if (!data.success) {
                setMessage(data.message || 'Invalid pincode.');
                return;
            }
            closeModal();
            window.location.reload();
        });
    }

    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.buyer-location-select');
        if (!btn) {
            return;
        }
        selectLocation({
            lat: Number(btn.dataset.lat),
            lng: Number(btn.dataset.lng),
            location_name: btn.dataset.name,
            pincode: btn.dataset.pincode || ''
        });
    });

    // Auto-open on first visit pages and when redirected for order location requirement.
    (async function initLocationPrompt() {
        const data = await fetchState();
        renderState(data);
        const shouldAutoOpen = data.show_modal && (window.location.pathname === '/buyers/' || window.location.pathname.startsWith('/buyers/search'));
        const locationRequired = new URLSearchParams(window.location.search).get('location_required') === '1';
        if (shouldAutoOpen || locationRequired) {
            openModal('Find meals near you');
            // Disable close/skip for buyers with no location
            if (data.show_modal && (!data.current || !data.current.lat || !data.current.lng)) {
                const closeBtn = document.getElementById('location-modal-close');
                if (closeBtn) closeBtn.style.display = 'none';
                const skipBtn = document.getElementById('location-skip-btn');
                if (skipBtn) skipBtn.style.display = 'none';
                setMessage('Location is required to use HomeFood. Please set your location.');
            }
            if (locationRequired) {
                setMessage('Please set your location to place an order.');
            }
        }
        // Re-enable close/skip after location is set
        if (data.current && data.current.lat && data.current.lng) {
            const closeBtn = document.getElementById('location-modal-close');
            if (closeBtn) closeBtn.style.display = '';
            const skipBtn = document.getElementById('location-skip-btn');
            if (skipBtn) skipBtn.style.display = '';
        }
    })();
})();
