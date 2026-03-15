from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import OperationalError, transaction
from .models import User, UserProfile, CookProfile
from .forms import UserRegistrationForm, UserProfileForm, CookProfileForm, CookRegistrationForm
from apps.buyers.location_utils import geocode_query, set_session_location


def _bootstrap_buyer_location_session(request, user):
    if user.user_type != 'buyer':
        return
    profile = getattr(user, 'user_profile', None)
    if not profile:
        return

    if request.session.get('buyer_lat') is not None and request.session.get('buyer_lng') is not None:
        return

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


def _apply_cook_geocode_from_pincode(cook_profile):
    # Keep manually-entered coordinates if already set.
    if cook_profile.latitude is not None and cook_profile.longitude is not None:
        return
    if not cook_profile.pincode:
        return

    result = geocode_query(cook_profile.pincode)
    if result:
        cook_profile.latitude = result['lat']
        cook_profile.longitude = result['lng']
        if not cook_profile.city:
            cook_profile.city = result.get('location_name', '')


def register(request):
    """
    User registration view. If registering as a cook, require address/location fields.
    This ensures every cook has location data for location-based meal discovery.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        cook_form = CookRegistrationForm(request.POST)
        user_type = request.POST.get('user_type')
        if form.is_valid() and (user_type != 'cook' or cook_form.is_valid()):
            try:
                with transaction.atomic():
                    user = form.save()
                    user.user_type = user_type
                    user.save()
                    # Create appropriate profile
                    if user_type == 'cook':
                        cook_profile = cook_form.save(commit=False)
                        cook_profile.user = user
                        cook_profile.verification_status = 'pending'
                        cook_profile.is_verified = False
                        _apply_cook_geocode_from_pincode(cook_profile)
                        cook_profile.save()
                    else:
                        UserProfile.objects.create(user=user)

                messages.success(request, 'Registration successful! Please login.')
                return redirect('accounts:login')
            except OperationalError:
                messages.error(
                    request,
                    'Database is busy right now. Please close any open SQLite tools and try again in a few seconds.'
                )
    else:
        form = UserRegistrationForm()
        cook_form = CookRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'cook_form': cook_form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            _bootstrap_buyer_location_session(request, user)
            # Redirect based on user type
            if user.user_type == 'cook':
                return redirect('cooks:dashboard')
            elif user.user_type == 'admin':
                return redirect('admin_panel:dashboard')
            elif user.user_type == 'buyer':
                # Check if location is set
                profile = getattr(user, 'user_profile', None)
                lat = profile.saved_lat if profile and profile.saved_lat is not None else (profile.latitude if profile and profile.latitude is not None else None)
                lng = profile.saved_lng if profile and profile.saved_lng is not None else (profile.longitude if profile and profile.longitude is not None else None)
                if lat is None or lng is None:
                    # Redirect to location setup page/modal
                    return redirect('buyers:home')
                else:
                    return redirect('buyers:home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """User logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def profile(request):
    """User profile view"""
    user = request.user
    if user.user_type == 'cook':
        profile_obj = getattr(user, 'cook_profile', None)
    else:
        profile_obj = getattr(user, 'user_profile', None)
    return render(request, 'accounts/profile.html', {'profile': profile_obj})


@login_required
def edit_profile(request):
    """Edit user profile"""
    user = request.user
    if user.user_type == 'cook':
        profile_obj = getattr(user, 'cook_profile', None)
        if not profile_obj:
            profile_obj = CookProfile.objects.create(user=user)
        form_class = CookProfileForm
    else:
        profile_obj = getattr(user, 'user_profile', None)
        if not profile_obj:
            profile_obj = UserProfile.objects.create(user=user)
        form_class = UserProfileForm
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            updated_profile = form.save(commit=False)
            if user.user_type != 'cook' and updated_profile.dietary_preferences is None:
                updated_profile.dietary_preferences = []
            if user.user_type == 'cook':
                _apply_cook_geocode_from_pincode(updated_profile)
            updated_profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = form_class(instance=profile_obj)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})






