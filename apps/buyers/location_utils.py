from __future__ import annotations

import math
from typing import Dict, List, Optional

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim


GEOCODER_USER_AGENT = 'homefood-location'


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two coordinates in km."""
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def _get_geolocator() -> Nominatim:
    return Nominatim(user_agent=GEOCODER_USER_AGENT, timeout=10)


def reverse_geocode(lat: float, lng: float) -> Dict[str, str]:
    """Resolve coordinates to a readable area name and optional pincode."""
    try:
        location = _get_geolocator().reverse((lat, lng), language='en', exactly_one=True)
    except (GeocoderTimedOut, GeocoderServiceError, ValueError):
        return {'location_name': f'{lat:.4f}, {lng:.4f}', 'pincode': ''}

    if not location:
        return {'location_name': f'{lat:.4f}, {lng:.4f}', 'pincode': ''}

    address = location.raw.get('address', {})
    location_name = (
        address.get('suburb')
        or address.get('neighbourhood')
        or address.get('city_district')
        or address.get('city')
        or address.get('town')
        or address.get('village')
        or location.address.split(',')[0]
    )
    return {
        'location_name': location_name or f'{lat:.4f}, {lng:.4f}',
        'pincode': address.get('postcode', ''),
    }


def geocode_query(query: str) -> Optional[Dict[str, str]]:
    """Geocode a pincode/address query to one location result."""
    if not query:
        return None
    try:
        location = _get_geolocator().geocode(query, exactly_one=True, language='en', country_codes='in')
    except (GeocoderTimedOut, GeocoderServiceError, ValueError):
        return None

    if not location:
        return None

    address = location.raw.get('address', {})
    location_name = (
        address.get('suburb')
        or address.get('neighbourhood')
        or address.get('city_district')
        or address.get('city')
        or address.get('town')
        or address.get('village')
        or location.address.split(',')[0]
    )
    return {
        'lat': float(location.latitude),
        'lng': float(location.longitude),
        'location_name': location_name or location.address.split(',')[0],
        'pincode': address.get('postcode', ''),
        'full_address': location.address,
    }


def geocode_suggestions(query: str, limit: int = 5) -> List[Dict[str, str]]:
    """Return multiple geocoding suggestions for manual area search."""
    if not query or len(query.strip()) < 3:
        return []
    try:
        results = _get_geolocator().geocode(
            query,
            exactly_one=False,
            limit=limit,
            language='en',
            country_codes='in',
            addressdetails=True,
        )
    except (GeocoderTimedOut, GeocoderServiceError, ValueError):
        return []

    if not results:
        return []

    suggestions = []
    for item in results:
        address = item.raw.get('address', {})
        location_name = (
            address.get('suburb')
            or address.get('neighbourhood')
            or address.get('city_district')
            or address.get('city')
            or address.get('town')
            or address.get('village')
            or item.address.split(',')[0]
        )
        suggestions.append({
            'label': item.address,
            'location_name': location_name or item.address.split(',')[0],
            'lat': float(item.latitude),
            'lng': float(item.longitude),
            'pincode': address.get('postcode', ''),
        })
    return suggestions


def session_location_payload(request) -> Optional[Dict[str, str]]:
    """Read active location from session if present and valid."""
    lat = request.session.get('buyer_lat')
    lng = request.session.get('buyer_lng')
    if lat is None or lng is None:
        return None
    return {
        'lat': float(lat),
        'lng': float(lng),
        'location_name': request.session.get('buyer_location_name', ''),
        'pincode': request.session.get('buyer_pincode', ''),
    }


def set_session_location(request, payload: Dict[str, str]) -> None:
    request.session['buyer_lat'] = float(payload['lat'])
    request.session['buyer_lng'] = float(payload['lng'])
    request.session['buyer_location_name'] = payload.get('location_name', '')
    request.session['buyer_pincode'] = payload.get('pincode', '')
    request.session['buyer_location_skipped'] = False
    request.session['buyer_location_prompt_dismissed'] = True


def clear_session_location(request) -> None:
    for key in ('buyer_lat', 'buyer_lng', 'buyer_location_name', 'buyer_pincode'):
        request.session.pop(key, None)
