// Home page location button now uses the shared location modal flow.
document.addEventListener('DOMContentLoaded', function() {
    const findNearbyBtn = document.getElementById('find-nearby-meals');
    if (!findNearbyBtn) {
        return;
    }
    findNearbyBtn.addEventListener('click', function() {
        const modal = document.getElementById('locationModal');
        const title = document.getElementById('location-modal-title');
        if (title) {
            title.textContent = 'Find meals near you';
        }
        if (modal) {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }
    });
});
