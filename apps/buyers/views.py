from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import math
# --- API endpoint for location-based filtering ---
@csrf_exempt
def api_nearby_meals(request):
    """
    API endpoint: POST { latitude, longitude }
    Returns approved cooks and their meals within 5-10 km radius.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST required.'}, status=405)
    import json
    try:
        data = json.loads(request.body)
        lat = float(data.get('latitude'))
        lng = float(data.get('longitude'))
    except Exception:
        return JsonResponse({'success': False, 'message': 'Invalid input.'}, status=400)

    # Haversine formula
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    radius_km = 12  # Increased radius to 12 km
    cooks = CookProfile.objects.filter(latitude__isnull=False, longitude__isnull=False)
    results = []
    for cook in cooks:
        if cook.latitude is None or cook.longitude is None:
            continue
        dist = haversine(lat, lng, float(cook.latitude), float(cook.longitude))
        if dist <= radius_km:
            meals = cook.meals.filter(is_available=True)
            for meal in meals:
                # Debug: print meal ID to terminal
                print(f"Nearby meal found: meal_id={meal.id}, meal_name={meal.name}, cook_id={cook.id}")
                # Try to get the first image URL if available
                image_url = None
                if hasattr(meal, 'images') and meal.images.first():
                    image_url = meal.images.first().image.url
                else:
                    image_url = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400'
                results.append({
                    'id': cook.id,
                    'name': cook.user.get_full_name() or cook.user.username,
                    'latitude': float(cook.latitude),
                    'longitude': float(cook.longitude),
                    'meal_name': meal.name,
                    'meal_id': meal.id,
                    'distance_km': round(dist, 2),
                    'image_url': image_url,
                    'description': meal.description,
                    'price': meal.price,
                    'is_available': meal.is_available,
                })
    return JsonResponse({'success': True, 'cooks': results})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from .models import BuyerOrder, BuyerReview, FavoriteCook, SearchHistory
from .forms import BuyerReviewForm
from apps.cooks.models import Meal, CookOrder, CookReview
from apps.accounts.models import CookProfile


def home(request):
    """Home page with featured meals and nearby cooks"""
    # Get available meals
    from datetime import date, datetime, time
    meals = []
    for meal in Meal.objects.filter(is_available=True).select_related('cook', 'cook__user').order_by('-created_at'):
        # Check for at least one active slot with available quantity and future date/time
        has_active_slot = False
        for slot in meal.pickup_slots.filter(is_active=True, available_quantity__gt=0):
            slot_datetime = datetime.combine(slot.date, slot.end_time)
            if slot_datetime > datetime.now():
                has_active_slot = True
                break
        meal.has_active_slot = has_active_slot
        meals.append(meal)
    meals = meals[:12]

    # Get all healthy/salad meals for Healthy Diets section
    from apps.cooks.models import HealthyDiet
    healthy_meals = Meal.objects.filter(meal_category='healthy', is_available=True).select_related('cook', 'cook__user').order_by('-created_at')
    # Try to get dietary tags from HealthyDiet if exists
    healthy_diets = []
    for meal in healthy_meals:
        diet = getattr(meal, 'healthy_diet', None)
        healthy_diets.append({
            'meal': meal,
            'dietary_tags': diet.dietary_tags if diet else [],
        })

    # Get verified cooks
    # Only show cooks with at least 1 review and rating > 0
    verified_cooks = CookProfile.objects.select_related('user').filter(rating__gt=0, total_reviews__gt=0).order_by('-rating', '-total_reviews')[:6]

    context = {
        'meals': meals,
        'healthy_diets': healthy_diets,
        'verified_cooks': verified_cooks,
    }
    return render(request, 'buyers/home.html', context)


def search(request):
    """Location-based meal search"""
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    
    meals = Meal.objects.filter(is_available=True).select_related('cook', 'cook__user')
    
    # Filter by query
    if query:
        meals = meals.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query)
        )
    
    # Filter by location (if coordinates provided)
    if lat and lng:
        try:
            lat = float(lat)
            lng = float(lng)
            # Simple distance filtering (can be improved with proper geospatial queries)
            # For now, we'll just show all meals and let user browse
            pass
        except ValueError:
            pass
    
    # Save search history if user is logged in
    if request.user.is_authenticated:
        SearchHistory.objects.create(
            buyer=request.user,
            query=query,
            location=location,
            latitude=lat if lat else None,
            longitude=lng if lng else None
        )
    
    context = {
        'meals': meals[:20],  # Limit results
        'query': query,
        'location': location,
    }
    return render(request, 'buyers/search.html', context)


def meal_detail(request, pk):
    """Meal detail page"""
    meal = get_object_or_404(Meal, pk=pk)
    from datetime import datetime
    pickup_slots = []
    for slot in meal.pickup_slots.filter(is_active=True, available_quantity__gt=0).order_by('date', 'start_time'):
        slot_datetime = datetime.combine(slot.date, slot.end_time)
        if slot_datetime > datetime.now():
            pickup_slots.append(slot)
    
    # Get reviews for this meal
    reviews = CookReview.objects.filter(order__meal=meal).order_by('-created_at')[:10]
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'meal': meal,
        'pickup_slots': pickup_slots,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
    }
    return render(request, 'buyers/meal_detail.html', context)


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
    
    if request.method == 'POST':
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
    
    context = {
        'order': order,
        'has_review': has_review,
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
            
            # Perform sentiment analysis on comment
            try:
                from apps.ml_engine.ml_services import SentimentAnalysisService
                sentiment_service = SentimentAnalysisService()
                if review.comment:
                    sentiment_score = sentiment_service.analyze(review.comment)
                    review.sentiment_score = sentiment_score
                    review.save()
            except Exception as e:
                # If ML service is not available, continue without sentiment analysis
                pass
            
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
                    comment=review.comment,
                    sentiment_score=review.sentiment_score
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


@login_required
def recommendations(request):
    """ML-based meal recommendations"""
    # Import ML service lazily to avoid heavy dependencies during Django checks/migrations
    from apps.ml_engine.ml_services import RecommendationService
    recommendation_service = RecommendationService()
    recommended_meals = recommendation_service.get_recommendations(request.user)
    
    context = {
        'recommended_meals': recommended_meals,
    }
    return render(request, 'buyers/recommendations.html', context)


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

