// JS for replacing featured meals with nearby meals if location is allowed

document.addEventListener('DOMContentLoaded', function() {
    const findNearbyBtn = document.getElementById('find-nearby-meals');
    const mealsGrid = document.querySelector('.meals-section .meals-grid');
    const sectionTitle = document.querySelector('.meals-section .section-title');
    const sectionSubtitle = document.querySelector('.meals-section .section-subtitle');

    function renderNearbyMeals(cooks) {
        if (!cooks.length) {
            mealsGrid.innerHTML = '<div class="meal-card"><div class="meal-card-content"><h3 class="meal-card-title">No meals found near you.</h3></div></div>';
            sectionTitle.textContent = 'Meals Near You';
            sectionSubtitle.textContent = 'No home-cooked meals found near your location.';
            return;
        }
        sectionTitle.textContent = 'Meals Near You';
        sectionSubtitle.textContent = 'Discover home-cooked meals from cooks near your location';
        mealsGrid.innerHTML = '';
        cooks.forEach(cook => {
            const card = document.createElement('div');
            card.className = 'meal-card';
            card.innerHTML = `
                <div class="meal-card-image">
                    <img src="${cook.image_url}" alt="${cook.meal_name}">
                    <span class="meal-card-badge">Available</span>
                </div>
                <div class="meal-card-content">
                    <h3 class="meal-card-title">${cook.meal_name}</h3>
                    <p class="meal-card-desc">${cook.description ? cook.description.substring(0, 60) + '...' : ''}</p>
                </div>
                <div class="meal-card-footer">
                    <span class="meal-price">₹${cook.price}</span>
                    <a href="/buyers/meals/${cook.meal_id}/" class="meal-btn">Buy Now</a>
                </div>
            `;
            mealsGrid.appendChild(card);
        });
    }

    function fetchNearbyMeals(lat, lng) {
        sectionTitle.textContent = 'Meals Near You';
        sectionSubtitle.textContent = 'Searching for home-cooked meals near your location...';
        mealsGrid.innerHTML = '<div class="meal-card"><div class="meal-card-content"><h3 class="meal-card-title">Loading...</h3></div></div>';
        fetch('/buyers/api/nearby-meals/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({latitude: lat, longitude: lng})
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderNearbyMeals(data.cooks);
            } else {
                mealsGrid.innerHTML = '<div class="meal-card"><div class="meal-card-content"><h3 class="meal-card-title">' + (data.message || 'No meals found.') + '</h3></div></div>';
            }
        })
        .catch(() => {
            mealsGrid.innerHTML = '<div class="meal-card"><div class="meal-card-content"><h3 class="meal-card-title">Error fetching meals.</h3></div></div>';
        });
    }

    if (findNearbyBtn) {
        findNearbyBtn.addEventListener('click', function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(pos) {
                    const lat = pos.coords.latitude;
                    const lng = pos.coords.longitude;
                    fetchNearbyMeals(lat, lng);
                }, function() {
                    // If denied, do nothing (keep featured meals)
                    alert('Location permission denied. Showing featured meals.');
                });
            } else {
                alert('Geolocation is not supported by your browser.');
            }
        });
    }
});
