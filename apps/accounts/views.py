from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, UserProfile, CookProfile
from .forms import UserRegistrationForm, UserProfileForm, CookProfileForm, CookRegistrationForm


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
            user = form.save()
            user.user_type = user_type
            user.save()
            # Create appropriate profile
            if user_type == 'cook':
                cook_profile = cook_form.save(commit=False)
                cook_profile.user = user
                cook_profile.save()
            else:
                UserProfile.objects.create(user=user)
            messages.success(request, 'Registration successful! Please login.')
            return redirect('accounts:login')
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
            # Redirect based on user type
            if user.user_type == 'cook':
                return redirect('cooks:dashboard')
            elif user.user_type == 'admin':
                return redirect('admin_panel:dashboard')
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
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = form_class(instance=profile_obj)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})






