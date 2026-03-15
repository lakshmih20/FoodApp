from django.conf import settings


def google_maps_api_key(request):
    """Context processor to add Google Maps API key to all templates"""
    buyer_active_location = None
    if request.user.is_authenticated and getattr(request.user, 'user_type', '') == 'buyer':
        lat = request.session.get('buyer_lat')
        lng = request.session.get('buyer_lng')
        if lat is not None and lng is not None:
            buyer_active_location = {
                'lat': float(lat),
                'lng': float(lng),
                'location_name': request.session.get('buyer_location_name', ''),
                'pincode': request.session.get('buyer_pincode', ''),
            }

    return {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
        'buyer_active_location': buyer_active_location,
    }






