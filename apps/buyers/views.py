from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
import json
from .models import BuyerOrder, BuyerReview, FavoriteCook, SearchHistory
from .forms import BuyerReviewForm
from apps.cooks.models import Meal, CookOrder, CookReview
from apps.accounts.models import CookProfile, UserProfile
from apps.admin_panel.models import Report
from .location_utils import (
    geocode_query,
    geocode_suggestions,
    haversine_km,
    reverse_geocode,
    session_location_payload,
    set_session_location,
)


RADIUS_OPTIONS = [2, 5, 10, 20]
DEFAULT_RADIUS = 10


def _get_or_create_buyer_profile(user):
    return UserProfile.objects.get_or_create(user=user)[0]


def _sync_session_location_from_profile(request):
    if not request.user.is_authenticated or request.user.user_type != 'buyer':
        return
    if request.session.get('buyer_lat') is not None and request.session.get('buyer_lng') is not None:
        return

    profile = _get_or_create_buyer_profile(request.user)
    lat = profile.saved_lat if profile.saved_lat is not None else profile.latitude
    lng = profile.saved_lng if profile.saved_lng is not None else profile.longitude
    if lat is None or lng is None:
        return
    set_session_location(request, {
        'lat': float(lat),
        'lng': float(lng),
        'location_name': profile.saved_location_name or profile.city or '',
        'pincode': profile.saved_pincode or profile.pincode or '',
    })


def _update_recent_locations(profile, new_location):
    existing = profile.recent_locations if isinstance(profile.recent_locations, list) else []
    deduped = [
        item for item in existing
        if not (
            str(item.get('location_name', '')).lower() == str(new_location.get('location_name', '')).lower()
            and abs(float(item.get('lat', 0)) - float(new_location.get('lat', 0))) < 0.0001
            and abs(float(item.get('lng', 0)) - float(new_location.get('lng', 0))) < 0.0001
        )
    ]
    deduped.insert(0, {
        'location_name': new_location.get('location_name', ''),
        'lat': float(new_location['lat']),
        'lng': float(new_location['lng']),
        'pincode': new_location.get('pincode', ''),
    })
    profile.recent_locations = deduped[:3]


def _save_location_for_buyer(request, location_payload):
    profile = _get_or_create_buyer_profile(request.user)

    previous = session_location_payload(request)
    if previous:
        _update_recent_locations(profile, previous)

    set_session_location(request, location_payload)
    # Always sync pincode and location to BuyerProfile
    profile.saved_lat = location_payload['lat']
    profile.saved_lng = location_payload['lng']
    profile.saved_location_name = location_payload.get('location_name', '')
    profile.saved_pincode = location_payload.get('pincode', '')
    profile.latitude = location_payload['lat']
    profile.longitude = location_payload['lng']
    if location_payload.get('location_name'):
        profile.city = location_payload['location_name']
    if location_payload.get('pincode'):
        profile.pincode = location_payload['pincode']
    profile.save()


def _meal_queryset_for_buyer_location(request, radius_km, include_query=None):
    base_qs = Meal.objects.filter(is_available=True, cook__is_verified=True).select_related('cook', 'cook__user')
    if include_query:
        base_qs = base_qs.filter(include_query)

    current_location = session_location_payload(request)
    if not current_location:
        return list(base_qs.order_by('-created_at')[:20]), False

    buyer_lat = float(current_location['lat'])
    buyer_lng = float(current_location['lng'])
    buyer_pincode = str((current_location.get('pincode') or '')).strip()
    filtered = []
    for meal in base_qs.order_by('-created_at'):
        cook_lat = meal.cook.latitude
        cook_lng = meal.cook.longitude
        cook_pincode = str((meal.cook.pincode or '')).strip()

        # If cook coordinates are missing, try geocoding from cook pincode once and persist.
        if cook_lat is None or cook_lng is None:
            if cook_pincode:
                geo = geocode_query(cook_pincode)
                if geo and geo.get('lat') is not None and geo.get('lng') is not None:
                    cook_lat = float(geo['lat'])
                    cook_lng = float(geo['lng'])
                    meal.cook.latitude = cook_lat
                    meal.cook.longitude = cook_lng
                    update_fields = ['latitude', 'longitude']
                    if not meal.cook.city and geo.get('location_name'):
                        meal.cook.city = geo.get('location_name')
                        update_fields.append('city')
                    meal.cook.save(update_fields=update_fields)

        # Last-resort fallback for nearby same-area pincodes when geocoding is unavailable.
        if cook_lat is None or cook_lng is None:
            if buyer_pincode and cook_pincode and buyer_pincode[:3] == cook_pincode[:3]:
                meal.distance_km = float(radius_km)
                filtered.append(meal)
            continue

        distance = haversine_km(buyer_lat, buyer_lng, float(cook_lat), float(cook_lng))
        if distance <= radius_km:
            meal.distance_km = round(distance, 1)
            filtered.append(meal)
    filtered.sort(key=lambda m: m.distance_km)
    return filtered, True


def home(request):
    """Home page with featured meals and nearby cooks"""
    from datetime import datetime

    _sync_session_location_from_profile(request)
    show_all = request.GET.get('show_all') == '1'
    radius = int(request.GET.get('radius', DEFAULT_RADIUS)) if str(request.GET.get('radius', DEFAULT_RADIUS)).isdigit() else DEFAULT_RADIUS
    radius = radius if radius in RADIUS_OPTIONS else DEFAULT_RADIUS

    # Get available meals (location-filtered when buyer location is set).
    meals, location_applied = _meal_queryset_for_buyer_location(request, radius_km=radius)
    if show_all:
        meals = list(Meal.objects.filter(is_available=True, cook__is_verified=True).select_related('cook', 'cook__user').order_by('-created_at')[:20])
        location_applied = False
    processed_meals = []
    for meal in meals:
        # Check for at least one active slot with available quantity and future date/time
        has_active_slot = False
        for slot in meal.pickup_slots.filter(is_active=True, available_quantity__gt=0):
            slot_datetime = datetime.combine(slot.date, slot.end_time)
            if slot_datetime > datetime.now():
                has_active_slot = True
                break
        meal.has_active_slot = has_active_slot
        processed_meals.append(meal)
    meals = processed_meals[:12]

    # Get all healthy/salad meals for Healthy Diets section
    healthy_diets = []
    for meal in Meal.objects.filter(is_available=True, cook__is_verified=True, meal_category='healthy').select_related('cook', 'cook__user'):
        healthy_diets.append({
            'meal': meal,
        })

    # Get verified cooks
    # Only show cooks with at least 1 review and rating > 0
    verified_cooks = CookProfile.objects.select_related('user').filter(rating__gt=0, total_reviews__gt=0).order_by('-rating', '-total_reviews')[:6]

    active_location = session_location_payload(request)
    should_show_location_modal = (
        request.user.is_authenticated
        and request.user.user_type == 'buyer'
        and not active_location
        and not request.session.get('buyer_location_prompt_dismissed', False)
        and request.path == '/buyers/'
    )

    context = {
        'meals': meals,
        'healthy_diets': healthy_diets,
        'verified_cooks': verified_cooks,
        'active_location': active_location,
        'radius_options': RADIUS_OPTIONS,
        'selected_radius': radius,
        'location_applied': location_applied,
        'location_missing': not bool(active_location),
        'show_location_modal': should_show_location_modal,
    }
    return render(request, 'buyers/home.html', context)


def search(request):
    """Location-based meal search"""
    _sync_session_location_from_profile(request)
    show_all = request.GET.get('show_all') == '1'
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    radius = int(request.GET.get('radius', DEFAULT_RADIUS)) if str(request.GET.get('radius', DEFAULT_RADIUS)).isdigit() else DEFAULT_RADIUS
    radius = radius if radius in RADIUS_OPTIONS else DEFAULT_RADIUS

    meals_query = Q()
    # Filter by query
    if query:
        meals_query &= (
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query)
        )

    meals, location_applied = _meal_queryset_for_buyer_location(request, radius_km=radius, include_query=meals_query)
    if show_all:
        meals = list(Meal.objects.filter(meals_query, is_available=True, cook__is_verified=True).select_related('cook', 'cook__user').order_by('-created_at')[:20])
        location_applied = False
    # Save search history if user is logged in
    if request.user.is_authenticated:
        active_location = session_location_payload(request)
        SearchHistory.objects.create(
            buyer=request.user,
            query=query,
            location=(active_location or {}).get('location_name', location),
            latitude=(active_location or {}).get('lat'),
            longitude=(active_location or {}).get('lng')
        )

    active_location = session_location_payload(request)
    should_show_location_modal = (
        request.user.is_authenticated
        and request.user.user_type == 'buyer'
        and not active_location
        and not request.session.get('buyer_location_prompt_dismissed', False)
        and request.path.startswith('/buyers/search')
    )

    context = {
        'meals': meals[:20],
        'query': query,
        'location': location,
        'active_location': active_location,
        'radius_options': RADIUS_OPTIONS,
        'selected_radius': radius,
        'location_applied': location_applied,
        'location_missing': not bool(active_location),
        'show_location_modal': should_show_location_modal,
    }
    return render(request, 'buyers/search.html', context)


@login_required
@require_GET
def location_state(request):
    if request.user.user_type != 'buyer':
        return JsonResponse({'success': False, 'message': 'Buyer account required.'}, status=403)
    _sync_session_location_from_profile(request)
    profile = _get_or_create_buyer_profile(request.user)
    current = session_location_payload(request)
    current_lat = (current or {}).get('lat')
    current_lng = (current or {}).get('lng')

    recent = []
    for item in profile.recent_locations[:3] if isinstance(profile.recent_locations, list) else []:
        distance = None
        if current and item.get('lat') is not None and item.get('lng') is not None:
            distance = round(
                haversine_km(float(current_lat), float(current_lng), float(item['lat']), float(item['lng'])),
                1,
            )
        recent.append({
            'location_name': item.get('location_name', ''),
            'lat': item.get('lat'),
            'lng': item.get('lng'),
            'pincode': item.get('pincode', ''),
            'distance_km': distance,
        })

    saved_addresses = []
    if profile.saved_lat is not None and profile.saved_lng is not None:
        saved_addresses.append({
            'label': profile.saved_location_name or 'Saved location',
            'location_name': profile.saved_location_name or 'Saved location',
            'lat': float(profile.saved_lat),
            'lng': float(profile.saved_lng),
            'pincode': profile.saved_pincode or '',
        })

    return JsonResponse({
        'success': True,
        'current': current,
        'recent_locations': recent,
        'saved_addresses': saved_addresses,
        'show_modal': not bool(current) and not request.session.get('buyer_location_prompt_dismissed', False),
    })


@login_required
@require_POST
def location_set_current(request):
    if request.user.user_type != 'buyer':
        return JsonResponse({'success': False, 'message': 'Buyer account required.'}, status=403)
    data = json.loads(request.body or '{}')
    try:
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'message': 'Invalid coordinates.'}, status=400)

    geo = reverse_geocode(lat, lng)
    payload = {
        'lat': lat,
        'lng': lng,
        'location_name': geo.get('location_name', ''),
        'pincode': geo.get('pincode', ''),
    }
    _save_location_for_buyer(request, payload)
    return JsonResponse({'success': True, 'location': payload})


@login_required
@require_POST
def location_set_pincode(request):
    if request.user.user_type != 'buyer':
        return JsonResponse({'success': False, 'message': 'Buyer account required.'}, status=403)
    data = json.loads(request.body or '{}')
    query = (data.get('pincode') or data.get('query') or '').strip()
    if not query:
        return JsonResponse({'success': False, 'message': 'Enter a pincode or area.'}, status=400)

    result = geocode_query(query)
    if not result:
        return JsonResponse({'success': False, 'message': 'Location not found. Try another pincode/area.'}, status=404)

    payload = {
        'lat': result['lat'],
        'lng': result['lng'],
        'location_name': result.get('location_name', query),
        'pincode': result.get('pincode', ''),
    }
    _save_location_for_buyer(request, payload)
    return JsonResponse({'success': True, 'location': payload})


@login_required
@require_GET
def location_search(request):
    if request.user.user_type != 'buyer':
        return JsonResponse({'success': False, 'message': 'Buyer account required.'}, status=403)
    query = request.GET.get('q', '').strip()
    return JsonResponse({'success': True, 'results': geocode_suggestions(query)})


@login_required
@require_POST
def location_select(request):
    if request.user.user_type != 'buyer':
        return JsonResponse({'success': False, 'message': 'Buyer account required.'}, status=403)
    data = json.loads(request.body or '{}')
    try:
        payload = {
            'lat': float(data.get('lat')),
            'lng': float(data.get('lng')),
            'location_name': (data.get('location_name') or '').strip(),
            'pincode': (data.get('pincode') or '').strip(),
        }
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'message': 'Invalid location selection.'}, status=400)
    if not payload['location_name']:
        payload['location_name'] = f"{payload['lat']:.4f}, {payload['lng']:.4f}"
    _save_location_for_buyer(request, payload)
    return JsonResponse({'success': True, 'location': payload})


@login_required
@require_POST
def location_skip(request):
    if request.user.user_type != 'buyer':
        return JsonResponse({'success': False, 'message': 'Buyer account required.'}, status=403)
    request.session['buyer_location_prompt_dismissed'] = True
    request.session['buyer_location_skipped'] = True
    return JsonResponse({'success': True})


@require_POST
def api_nearby_meals(request):
    """API endpoint: returns meals within selected radius sorted by nearest first."""
    if request.user.is_authenticated and request.user.user_type == 'buyer':
        _sync_session_location_from_profile(request)

    data = json.loads(request.body or '{}')
    radius_km = int(data.get('radius', DEFAULT_RADIUS)) if str(data.get('radius', DEFAULT_RADIUS)).isdigit() else DEFAULT_RADIUS
    radius_km = radius_km if radius_km in RADIUS_OPTIONS else DEFAULT_RADIUS

    try:
        lat = float(data.get('latitude')) if data.get('latitude') is not None else None
        lng = float(data.get('longitude')) if data.get('longitude') is not None else None
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'message': 'Invalid input.'}, status=400)

    if lat is None or lng is None:
        session_loc = session_location_payload(request)
        if not session_loc:
            return JsonResponse({'success': True, 'cooks': [], 'message': 'Location not set.'})
        lat = float(session_loc['lat'])
        lng = float(session_loc['lng'])

    cooks = CookProfile.objects.filter(latitude__isnull=False, longitude__isnull=False, is_verified=True)
    results = []
    for cook in cooks:
        distance = haversine_km(lat, lng, float(cook.latitude), float(cook.longitude))
        if distance > radius_km:
            continue
        for meal in cook.meals.filter(is_available=True):
            image_url = meal.images.first().image.url if hasattr(meal, 'images') and meal.images.first() else 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400'
            results.append({
                'id': cook.id,
                'name': cook.user.get_full_name() or cook.user.username,
                'latitude': float(cook.latitude),
                'longitude': float(cook.longitude),
                'meal_name': meal.name,
                'meal_id': meal.id,
                'distance_km': round(distance, 1),
                'image_url': image_url,
                'description': meal.description,
                'price': float(meal.price),
                'is_available': meal.is_available,
            })
    results.sort(key=lambda x: x['distance_km'])
    return JsonResponse({'success': True, 'cooks': results})


def meal_detail(request, pk):
    """Meal detail page"""
    _sync_session_location_from_profile(request)
    meal = get_object_or_404(Meal, pk=pk, cook__is_verified=True)
    from datetime import date, timedelta

    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Try today's slots first
    todays_slots = meal.pickup_slots.filter(
        date=today,
        is_active=True,
        available_quantity__gt=0
    ).order_by('start_time')

    if todays_slots.exists():
        upcoming_slots = todays_slots[:5]
        slot_date_label = "Today — " + today.strftime("%d %b %Y")
    else:
        tomorrows_slots = meal.pickup_slots.filter(
            date=tomorrow,
            is_active=True,
            available_quantity__gt=0
        ).order_by('start_time')
        upcoming_slots = tomorrows_slots[:5]
        if upcoming_slots:
            slot_date_label = "Tomorrow — " + tomorrow.strftime("%d %b %Y")
        else:
            slot_date_label = None

    # Total available portions across the shown slots
    total_portions = sum(slot.available_quantity for slot in upcoming_slots)

    # Keep pickup_slots for backward-compat (used in stats row)
    pickup_slots = list(upcoming_slots)

    # Get reviews for this meal
    reviews = CookReview.objects.filter(order__meal=meal).order_by('-created_at')[:10]

    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    # Attach live stream (if any) for this cook
    from apps.live_streaming.models import LiveStream
    live_stream = LiveStream.objects.filter(cook=meal.cook, status='live').first()

    # Split ingredients string by comma
    ingredients = [i.strip() for i in meal.ingredients.split(',') if i.strip()]

    context = {
        'meal': meal,
        'pickup_slots': pickup_slots,
        'upcoming_slots': upcoming_slots,
        'slot_date_label': slot_date_label,
        'total_portions': total_portions,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'live_stream': live_stream,
        'ingredients': ingredients,
        'report_orders': BuyerOrder.objects.filter(buyer=request.user, meal=meal).order_by('-created_at') if request.user.is_authenticated else [],
        'active_location': session_location_payload(request),
        'location_required_popup': request.GET.get('location_required') == '1',
    }
    return render(request, 'buyers/meal_detail.html', context)


@login_required
def create_report(request, meal_id):
    meal = get_object_or_404(Meal, pk=meal_id)
    if request.method != 'POST':
        return redirect('buyers:meal_detail', pk=meal_id)

    order_id = request.POST.get('order_id')
    reason = request.POST.get('reason')
    description = request.POST.get('description', '').strip()

    order = get_object_or_404(BuyerOrder, pk=order_id, buyer=request.user, meal=meal)

    if not reason or not description:
        messages.error(request, 'Please provide reason and description.')
        return redirect('buyers:meal_detail', pk=meal_id)

    Report.objects.create(
        buyer=request.user,
        cook=meal.cook,
        order=order,
        reason=reason,
        description=description,
    )
    messages.success(request, 'Report submitted to admin successfully.')
    return redirect('buyers:meal_detail', pk=meal_id)


def cook_profile(request, cook_id):
    """Cook profile page"""
    cook = get_object_or_404(CookProfile, pk=cook_id)
    meals = Meal.objects.filter(cook=cook, is_available=True).order_by('-created_at')
    
    # Get reviews
    reviews = CookReview.objects.filter(order__meal__cook=cook).order_by('-created_at')[:10]
    
    # Check if favorited
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = FavoriteCook.objects.filter(buyer=request.user, cook=cook).exists()
    
    context = {
        'cook': cook,
        'meals': meals,
        'reviews': reviews,
        'is_favorited': is_favorited,
    }
    return render(request, 'buyers/cook_profile.html', context)


@login_required
def create_order(request, meal_id):
    """Create an order"""
    meal = get_object_or_404(Meal, pk=meal_id, is_available=True)
    _sync_session_location_from_profile(request)
    
    if request.method == 'POST':
        active_location = session_location_payload(request)
        if not active_location:
            messages.error(request, 'Please set your location to place an order.')
            return redirect(f"{redirect('buyers:meal_detail', pk=meal_id).url}?location_required=1")

        pickup_slot_id = request.POST.get('pickup_slot')
        quantity = int(request.POST.get('quantity', 1))
        payment_method = request.POST.get('payment_method', 'cash')
        special_instructions = request.POST.get('special_instructions', '')
        
        pickup_slot = get_object_or_404(meal.pickup_slots, pk=pickup_slot_id, is_active=True)
        
        if pickup_slot.available_quantity < quantity:
            messages.error(request, 'Not enough quantity available for this slot.')
            return redirect('buyers:meal_detail', pk=meal_id)
        
        # Create BuyerOrder
        order = BuyerOrder.objects.create(
            buyer=request.user,
            meal=meal,
            cook=meal.cook,
            pickup_slot=pickup_slot,
            quantity=quantity,
            total_amount=meal.price * quantity,
            payment_method=payment_method,
            special_instructions=special_instructions
        )
        
        # Also create CookOrder for cook's view (they share the same order)
        from apps.cooks.models import CookOrder
        cook_order = CookOrder.objects.create(
            buyer=request.user,
            meal=meal,
            pickup_slot=pickup_slot,
            quantity=quantity,
            total_amount=meal.price * quantity,
            payment_status='pending' if payment_method == 'cash' else 'pending',
            status='pending'
        )
        
        # If online payment, redirect to payment page
        if payment_method == 'online':
            return redirect('payments:process', order_id=order.id)
        
        messages.success(request, 'Order placed successfully!')
        return redirect('buyers:order_detail', pk=order.id)
    
    return redirect('buyers:meal_detail', pk=meal_id)


@login_required
def order_list(request):
    """List buyer's orders"""
    orders = BuyerOrder.objects.filter(buyer=request.user).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    return render(request, 'buyers/order_list.html', {'orders': orders, 'status_filter': status_filter})


@login_required
def order_detail(request, pk):
    """Order detail page"""
    order = get_object_or_404(BuyerOrder, pk=pk, buyer=request.user)
    
    # Check if review exists
    has_review = BuyerReview.objects.filter(order=order).exists()
    
    # Attach any live stream linked to this order
    from apps.live_streaming.models import LiveStream
    live_stream = LiveStream.objects.filter(order=order, status='live').first()
    # Fallback: show cook's current live stream even if not linked to order
    if not live_stream:
        live_stream = LiveStream.objects.filter(cook=order.cook, status='live').first()

    context = {
        'order': order,
        'has_review': has_review,
        'live_stream': live_stream,
    }
    return render(request, 'buyers/order_detail.html', context)


@login_required
def add_review(request, pk):
    """Add questionnaire-based review for an order with food photos"""
    order = get_object_or_404(BuyerOrder, pk=pk, buyer=request.user)
    
    if order.status != 'completed':
        messages.error(request, 'You can only review completed orders.')
        return redirect('buyers:order_detail', pk=pk)
    
    if BuyerReview.objects.filter(order=order).exists():
        messages.error(request, 'You have already reviewed this order.')
        return redirect('buyers:order_detail', pk=pk)
    
    if request.method == 'POST':
        form = BuyerReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.save()
            
            # Sentiment analysis removed; review saved without ML
            
            # Also create CookReview (find the corresponding CookOrder)
            cook_order = CookOrder.objects.filter(
                buyer=order.buyer,
                meal=order.meal,
                pickup_slot=order.pickup_slot,
                created_at__date=order.created_at.date()
            ).first()
            
            if cook_order and not CookReview.objects.filter(order=cook_order).exists():
                CookReview.objects.create(
                    order=cook_order,
                    rating=review.overall_rating,
                    comment=review.comment
                )
            
            # Update cook rating
            cook = order.cook
            avg_rating = CookReview.objects.filter(order__meal__cook=cook).aggregate(Avg('rating'))['rating__avg'] or 0
            cook.rating = round(avg_rating, 2)
            cook.total_reviews = CookReview.objects.filter(order__meal__cook=cook).count()
            cook.save()
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('buyers:order_detail', pk=pk)
    else:
        form = BuyerReviewForm()
    
    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'buyers/add_review.html', context)


@login_required
def favorites(request):
    """View favorite cooks"""
    favorite_cooks = CookProfile.objects.filter(
        favorited_by__buyer=request.user
    ).select_related('user')
    
    return render(request, 'buyers/favorites.html', {'favorite_cooks': favorite_cooks})


@login_required
def add_favorite(request, cook_id):
    """Add cook to favorites"""
    cook = get_object_or_404(CookProfile, pk=cook_id)
    
    favorite, created = FavoriteCook.objects.get_or_create(
        buyer=request.user,
        cook=cook
    )
    
    if created:
        messages.success(request, f'{cook.user.username} added to favorites!')
    else:
        messages.info(request, f'{cook.user.username} is already in your favorites.')
    
    return redirect('buyers:cook_profile', cook_id=cook_id)


def recommendations(request):

    pass


@login_required
def buyer_nearby(request):
    """
    Nearby cooks page:
    - asks for location in the browser
    - shows Google Map + list of nearby cooks and meals
    """
    if request.user.user_type != 'buyer':
        messages.error(request, 'Buyer account required to view nearby cooks.')
        return redirect('buyers:home')

    # Radius options in km
    radius_options = [2, 5, 10]
    default_radius = 5

    context = {
        'radius_options': radius_options,
        'default_radius': default_radius,
    }
    return render(request, 'buyers/nearby.html', context)

