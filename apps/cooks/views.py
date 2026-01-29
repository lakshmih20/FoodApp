from django.contrib.auth.decorators import login_required
from .forms import CookFSSAICertificateForm

# Cook FSSAI certificate upload/update view
@login_required
def fssai_certificate_upload(request):
    if request.user.user_type != 'cook':
        messages.error(request, 'Access denied.')
        return redirect('buyers:home')

    cook_profile = get_object_or_404(CookProfile, user=request.user)
    if request.method == 'POST':
        form = CookFSSAICertificateForm(request.POST, request.FILES, instance=cook_profile)
        if form.is_valid():
            cook_profile = form.save(commit=False)
            # Removed status/risk logic
            cook_profile.save()
            messages.success(request, 'Certificate uploaded. Awaiting admin verification.')
            return redirect('cooks:dashboard')
    else:
        form = CookFSSAICertificateForm(instance=cook_profile)
    return render(request, 'accounts/edit_fssai_certificate.html', {'form': form, 'cook_profile': cook_profile})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from math import radians, sin, cos, asin, sqrt
from .models import Meal, MealImage, PickupSlot, CookOrder, CookReview, CookAnalytics
from .forms import MealForm, MealImageForm, PickupSlotForm
from apps.accounts.models import CookProfile


@login_required
def dashboard(request):
    """Cook dashboard with overview"""
    if request.user.user_type != 'cook':
        messages.error(request, 'Access denied. Cook access required.')
        return redirect('buyers:home')
    
    cook_profile = get_object_or_404(CookProfile, user=request.user)
    
    # Statistics
    total_meals = Meal.objects.filter(cook=cook_profile).count()
    active_meals = Meal.objects.filter(cook=cook_profile, is_available=True).count()
    
    # Recent orders
    recent_orders = CookOrder.objects.filter(meal__cook=cook_profile).order_by('-created_at')[:5]
    
    # Today's stats
    today = timezone.now().date()
    today_orders = CookOrder.objects.filter(
        meal__cook=cook_profile,
        created_at__date=today
    )
    today_revenue = today_orders.filter(payment_status='paid').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Pending orders
    pending_orders = CookOrder.objects.filter(
        meal__cook=cook_profile,
        status='pending'
    ).count()
    
    context = {
        'cook_profile': cook_profile,
        'total_meals': total_meals,
        'active_meals': active_meals,
        'recent_orders': recent_orders,
        'today_revenue': today_revenue,
        'today_orders_count': today_orders.count(),
        'pending_orders': pending_orders,
    }
    return render(request, 'cooks/dashboard.html', context)


@login_required
def meal_list(request):
    """List all meals for the cook"""
    if request.user.user_type != 'cook':
        messages.error(request, 'Access denied.')
        return redirect('buyers:home')
    
    cook_profile = get_object_or_404(CookProfile, user=request.user)
    meals = Meal.objects.filter(cook=cook_profile).order_by('-created_at')
    return render(request, 'cooks/meal_list.html', {'meals': meals})


@login_required
def meal_create(request):
    """Create a new meal"""
    if request.user.user_type != 'cook':
        messages.error(request, 'Access denied.')
        return redirect('buyers:home')
    
    cook_profile = get_object_or_404(CookProfile, user=request.user)

    if request.method == 'POST':
        form = MealForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.cook = cook_profile
            meal.save()
            # Handle images
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                MealImage.objects.create(
                    meal=meal,
                    image=image,
                    is_primary=(i == 0)
                )
            messages.success(request, 'Meal created successfully!')
            return redirect('cooks:meals')
    else:
        form = MealForm()
    return render(request, 'cooks/meal_form.html', {'form': form, 'action': 'Create'})


@login_required
def meal_edit(request, pk):
    """Edit an existing meal"""
    if request.user.user_type != 'cook':
        messages.error(request, 'Access denied.')
        return redirect('buyers:home')
    
    cook_profile = get_object_or_404(CookProfile, user=request.user)
    meal = get_object_or_404(Meal, pk=pk, cook=cook_profile)
    
    if request.method == 'POST':
        form = MealForm(request.POST, instance=meal)
        if form.is_valid():
            form.save()
            
            # Handle new images
            images = request.FILES.getlist('images')
            for image in images:
                MealImage.objects.create(meal=meal, image=image)
            
            messages.success(request, 'Meal updated successfully!')
            return redirect('cooks:meals')
    else:
        form = MealForm(instance=meal)
    
    existing_images = meal.images.all()
    return render(request, 'cooks/meal_form.html', {
        'form': form,
        'meal': meal,
        'existing_images': existing_images,
        'action': 'Edit'
    })


@login_required
def meal_delete(request, pk):
    """Delete a meal"""
    if request.user.user_type != 'cook':
        messages.error(request, 'Access denied.')
        return redirect('buyers:home')
    
    cook_profile = get_object_or_404(CookProfile, user=request.user)
    meal = get_object_or_404(Meal, pk=pk, cook=cook_profile)
    
    if request.method == 'POST':
        meal.delete()
        messages.success(request, 'Meal deleted successfully!')
        return redirect('cooks:meals')
    
    return render(request, 'cooks/meal_confirm_delete.html', {'meal': meal})


@login_required
def pickup_slots(request, meal_id):
    """Manage pickup slots for a meal"""
    if request.user.user_type != 'cook':
        messages.error(request, 'Access denied.')
        return redirect('buyers:home')
    
    cook_profile = get_object_or_404(CookProfile, user=request.user)
    meal = get_object_or_404(Meal, pk=meal_id, cook=cook_profile)
    
    if request.method == 'POST':
        form = PickupSlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.meal = meal
            slot.save()
            messages.success(request, 'Pickup slot created!')
            return redirect('cooks:pickup_slots', meal_id=meal_id)
    else:
        form = PickupSlotForm()
    
    slots = PickupSlot.objects.filter(meal=meal).order_by('date', 'start_time')
    return render(request, 'cooks/pickup_slots.html', {
        'meal': meal,
        'slots': slots,
        'form': form
    })


@login_required
def order_list(request):
    """List all orders for the cook"""
    if request.user.user_type != 'cook':
        messages.error(request, 'Access denied.')
        return redirect('buyers:home')
    
    cook_profile = get_object_or_404(CookProfile, user=request.user)
    orders = CookOrder.objects.filter(meal__cook=cook_profile).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    return render(request, 'cooks/order_list.html', {'orders': orders, 'status_filter': status_filter})


@login_required
def order_accept(request, pk):
    """Accept an order"""
    if request.user.user_type != 'cook':
        messages.error(request, 'Access denied.')
        return redirect('buyers:home')
    
    cook_profile = get_object_or_404(CookProfile, user=request.user)
    order = get_object_or_404(CookOrder, pk=pk, meal__cook=cook_profile)
    
    if order.status != 'pending':
        messages.error(request, 'Order cannot be accepted.')
        return redirect('cooks:orders')
    
    order.status = 'accepted'
    order.save()
    
    # Update pickup slot availability
    order.pickup_slot.available_quantity -= order.quantity
    order.pickup_slot.save()
    
    messages.success(request, 'Order accepted!')
    return redirect('cooks:orders')


@login_required
def order_reject(request, pk):
    """Reject an order"""
    if request.user.user_type != 'cook':
        messages.error(request, 'Access denied.')
        return redirect('buyers:home')
    
    cook_profile = get_object_or_404(CookProfile, user=request.user)
    order = get_object_or_404(CookOrder, pk=pk, meal__cook=cook_profile)
    
    if order.status != 'pending':
        messages.error(request, 'Order cannot be rejected.')
        return redirect('cooks:orders')
    
    order.status = 'rejected'
    order.save()
    
    messages.success(request, 'Order rejected.')
    return redirect('cooks:orders')


@login_required
def order_update_status(request, pk):
    """Update order status"""
    if request.user.user_type != 'cook':
        messages.error(request, 'Access denied.')
        return redirect('buyers:home')
    
    cook_profile = get_object_or_404(CookProfile, user=request.user)
    order = get_object_or_404(CookOrder, pk=pk, meal__cook=cook_profile)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(CookOrder.ORDER_STATUS):
            order.status = new_status
            order.save()
            messages.success(request, 'Order status updated!')
    
    return redirect('cooks:orders')


@login_required
def analytics(request):
    """Cook analytics dashboard"""
    if request.user.user_type != 'cook':
        messages.error(request, 'Access denied.')
        return redirect('buyers:home')
    
    cook_profile = get_object_or_404(CookProfile, user=request.user)
    
    # Get last 30 days of data
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    analytics_data = CookAnalytics.objects.filter(
        cook=cook_profile,
        date__range=[start_date, end_date]
    ).order_by('date')
    
    # Calculate totals
    total_revenue = analytics_data.aggregate(Sum('revenue'))['revenue__sum'] or 0
    total_orders = analytics_data.aggregate(Sum('orders_count'))['orders_count__sum'] or 0
    
    # Average rating
    avg_rating = CookReview.objects.filter(
        order__meal__cook=cook_profile
    ).aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'cook_profile': cook_profile,
        'analytics_data': analytics_data,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_rating': round(avg_rating, 2),
    }
    return render(request, 'cooks/analytics.html', context)


@login_required
def reviews(request):
    """View all reviews for cook's meals"""
    if request.user.user_type != 'cook':
        messages.error(request, 'Access denied.')
        return redirect('buyers:home')
    
    cook_profile = get_object_or_404(CookProfile, user=request.user)
    from apps.buyers.models import BuyerReview
    # Get all BuyerReview objects for orders where the cook is this cook
    reviews = BuyerReview.objects.filter(order__cook=cook_profile).order_by('-created_at')
    return render(request, 'cooks/reviews.html', {'reviews': reviews})


def _haversine_distance_km(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth (in km).
    Uses the Haversine formula.
    """
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


def nearby_cooks(request):
    """
    Public API: return nearby cooks with currently available meals.

    Expected query params:
    - lat: buyer latitude
    - lng: buyer longitude
    - radius_km: search radius in km (default 5)
    - available_only: '1' or 'true' to filter by availability (default on)
    """
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid or missing lat/lng'}, status=400)

    try:
        radius_km = float(request.GET.get('radius_km', 5))
    except ValueError:
        radius_km = 5.0

    available_only_param = request.GET.get('available_only', '1').lower()
    available_only = available_only_param in ['1', 'true', 'yes']

    # Base queryset: cooks with coordinates set and approved
    cooks_qs = CookProfile.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
        verification_status='approved',
    )

    if available_only:
        # Cook is marked available and has at least one active/available meal
        cooks_qs = cooks_qs.filter(
            is_available_now=True,
            meals__is_available=True,
            meals__pickup_slots__is_active=True,
            meals__pickup_slots__available_quantity__gt=0,
        ).distinct()

    results = []

    for cook in cooks_qs.select_related('user').prefetch_related('meals__pickup_slots'):
        if cook.latitude is None or cook.longitude is None:
            continue

        distance_km = _haversine_distance_km(
            lat,
            lng,
            cook.latitude,
            cook.longitude,
        )

        if distance_km > radius_km:
            continue

        # Build available meals list
        meals_data = []
        meals_qs = cook.meals.filter(is_available=True)
        if available_only:
            meals_qs = meals_qs.filter(
                pickup_slots__is_active=True,
                pickup_slots__available_quantity__gt=0,
            ).distinct()

        for meal in meals_qs:
            meals_data.append(
                {
                    'id': meal.id,
                    'name': meal.name,
                    'description': meal.description,
                    'price': float(meal.price),
                    'is_available': meal.is_available,
                }
            )

        if not meals_data:
            # Skip cooks with no meals to show
            continue

        results.append(
            {
                'id': cook.id,
                'name': cook.user.get_full_name() or cook.user.username,
                'lat': float(cook.latitude),
                'lng': float(cook.longitude),
                'address': cook.address,
                'city': cook.city,
                'rating': float(cook.rating),
                'total_reviews': cook.total_reviews,
                'distance_km': round(distance_km, 2),
                'is_available_now': cook.is_available_now,
                'meals': meals_data,
            }
        )

    # Sort by distance then rating desc
    results.sort(key=lambda c: (c['distance_km'], -c['rating']))

    return JsonResponse({'cooks': results})


@login_required
def create_order(request):
    """
    Public API for buyers to create an order for a specific meal and pickup slot.
    Expects POST JSON:
    - meal_id
    - pickup_slot_id
    - quantity
    - special_instructions (optional)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    if request.user.user_type != 'buyer':
        return JsonResponse({'error': 'Buyer account required'}, status=403)

    try:
        data = request.json if hasattr(request, 'json') else None
    except Exception:
        data = None

    if not data:
        # Fallback to parsing from body when request.json isn't available
        import json

        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    meal_id = data.get('meal_id')
    pickup_slot_id = data.get('pickup_slot_id')
    quantity = data.get('quantity', 1)
    special_instructions = data.get('special_instructions', '')

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid quantity'}, status=400)

    meal = get_object_or_404(Meal, id=meal_id, is_available=True)
    pickup_slot = get_object_or_404(
        PickupSlot,
        id=pickup_slot_id,
        meal=meal,
        is_active=True,
    )

    # Check availability
    if pickup_slot.available_quantity < quantity:
        return JsonResponse({'error': 'Not enough quantity available'}, status=400)

    cook_profile = meal.cook
    if not cook_profile.is_available_now or cook_profile.verification_status != 'approved':
        return JsonResponse({'error': 'Cook is not currently available'}, status=400)

    total_amount = meal.price * quantity

    order = CookOrder.objects.create(
        buyer=request.user,
        meal=meal,
        pickup_slot=pickup_slot,
        quantity=quantity,
        total_amount=total_amount,
        special_instructions=special_instructions,
    )

    # Decrease available quantity for the slot
    pickup_slot.available_quantity -= quantity
    if pickup_slot.available_quantity < 0:
        pickup_slot.available_quantity = 0
    pickup_slot.save()

    response_data = {
        'order_id': order.id,
        'status': order.status,
        'payment_status': order.payment_status,
        'pickup': {
            'date': pickup_slot.date.isoformat(),
            'start_time': pickup_slot.start_time.strftime('%H:%M'),
            'end_time': pickup_slot.end_time.strftime('%H:%M'),
            'address': cook_profile.address,
            'city': cook_profile.city,
        },
        'cook': {
            'id': cook_profile.id,
            'name': cook_profile.user.get_full_name() or cook_profile.user.username,
        },
        'meal': {
            'id': meal.id,
            'name': meal.name,
            'price': float(meal.price),
        },
    }

    return JsonResponse(response_data, status=201)
