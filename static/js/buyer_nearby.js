// JavaScript for buyers/nearby.html to fetch and display nearby meals

document.addEventListener('DOMContentLoaded', function() {
    const cooksList = document.getElementById('cooksList');
    const locationMessage = document.getElementById('location-message');
    const radiusSelect = document.getElementById('radiusSelect');
    const availableOnly = document.getElementById('availableOnly');

    function showMessage(msg, type='info') {
        locationMessage.textContent = msg;
        locationMessage.className = 'alert alert-' + type + ' small';
    }

    function renderCooks(cooks) {
        cooksList.innerHTML = '';
        if (!cooks.length) {
            cooksList.innerHTML = '<li class="list-group-item text-muted small">No meals found nearby.</li>';
            return;
        }
        cooks.forEach(cook => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.innerHTML = `
                <div class="d-flex align-items-center">
                    <img src="${cook.image_url}" alt="Meal" style="width: 56px; height: 56px; object-fit: cover; border-radius: 8px; margin-right: 12px;">
                    <div>
                        <strong>${cook.meal_name}</strong> <span class="badge bg-success">${cook.price} ₹</span><br>
                        <span class="text-muted small">by ${cook.name} (${cook.distance_km} km)</span>
                    </div>
                </div>
            `;
            cooksList.appendChild(li);
        });
    }

    function fetchNearbyMeals(lat, lng) {
        showMessage('Searching for nearby meals...');
        fetch('/buyers/api/nearby_meals/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({latitude: lat, longitude: lng})
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderCooks(data.cooks);
                showMessage('Showing meals near you!', 'success');
            } else {
                showMessage(data.message || 'No meals found.', 'warning');
            }
        })
        .catch(() => showMessage('Error fetching meals.', 'danger'));
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(pos) {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            fetchNearbyMeals(lat, lng);
        }, function() {
            showMessage('Location permission denied. Cannot find nearby meals.', 'danger');
        });
    } else {
        showMessage('Geolocation is not supported by your browser.', 'danger');
    }
});
