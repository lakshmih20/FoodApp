from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User, CookProfile, UserProfile
from apps.cooks.models import Meal, CookOrder
from apps.buyers.models import BuyerOrder
from apps.payments.models import Payment


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_staff or user.user_type == 'admin')


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard"""
    # Statistics
    total_users = User.objects.count()
    total_cooks = CookProfile.objects.count()
    verified_cooks = CookProfile.objects.count()  # No status field, so just count all
    pending_verifications = 0
    
    # Orders
    total_orders = BuyerOrder.objects.count()
    today_orders = BuyerOrder.objects.filter(created_at__date=timezone.now().date()).count()
    today_revenue = Payment.objects.filter(
        created_at__date=timezone.now().date(),
        status='success'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # Recent activities
    recent_orders = BuyerOrder.objects.order_by('-created_at')[:10]
    pending_cooks = CookProfile.objects.filter(verification_status='pending').order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'total_cooks': total_cooks,
        'verified_cooks': verified_cooks,
        'pending_verifications': pending_verifications,
        'total_orders': total_orders,
        'today_orders': today_orders,
        'today_revenue': today_revenue,
        'recent_orders': recent_orders,
        'pending_cooks': pending_cooks,
    }
    return render(request, 'admin_panel/dashboard.html', context)



@login_required
@user_passes_test(is_admin)
def cook_verification_list(request):
    """List cooks pending verification"""
    pending_cooks = CookProfile.objects.filter(verification_status='pending').order_by('-created_at')
    return render(request, 'admin_panel/cook_verification_list.html', {'pending_cooks': pending_cooks})



@login_required
@user_passes_test(is_admin)
def verify_cook(request, cook_id):
    """Approve cook verification"""
    cook = get_object_or_404(CookProfile, pk=cook_id)
    cook.verification_status = 'approved'
    cook.fssai_certificate_status = 'approved'
    cook.certificate_verification_date = timezone.now()
    cook.save()
    messages.success(request, f'Cook {cook.user.username} has been FSSAI verified.')
    return redirect('admin_panel:cook_verification_list')


@login_required
@user_passes_test(is_admin)
def reject_cook(request, cook_id):
    """Reject cook verification"""
    cook = get_object_or_404(CookProfile, pk=cook_id)
    cook.save()
    messages.success(request, f'Cook {cook.user.username} FSSAI verification has been rejected.')
    return redirect('admin_panel:cook_verification_list')

@login_required
@user_passes_test(is_admin)
def user_list(request):
    """List all users"""
    users = User.objects.all().order_by('-date_joined')
    
    # Filter by type
    user_type = request.GET.get('type')
    if user_type:
        users = users.filter(user_type=user_type)
    
    return render(request, 'admin_panel/user_list.html', {'users': users, 'user_type_filter': user_type})


@login_required
@user_passes_test(is_admin)
def order_list(request):
    """List all orders"""
    orders = BuyerOrder.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    return render(request, 'admin_panel/order_list.html', {'orders': orders, 'status_filter': status_filter})


@login_required
@user_passes_test(is_admin)
def dispute_list(request):
    """List disputes and complaints"""
    # This would typically come from a Dispute model
    # For now, we'll show cancelled orders as disputes
    disputes = BuyerOrder.objects.filter(status='cancelled').order_by('-created_at')
    return render(request, 'admin_panel/dispute_list.html', {'disputes': disputes})


@login_required
@user_passes_test(is_admin)
def analytics(request):
    """Platform-wide analytics"""
    # Date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Revenue trends from payments
    daily_revenue = Payment.objects.filter(
        created_at__date__range=[start_date, end_date],
        status='success'
    ).extra(
        select={'day': 'DATE(created_at)'}
    ).values('day').annotate(
        revenue=Sum('amount')
    ).order_by('day')
    
    # Order trends
    daily_orders = BuyerOrder.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).extra(
        select={'day': 'DATE(created_at)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Top cooks
    top_cooks = CookProfile.objects.annotate(
        order_count=Count('buyer_orders')
    ).order_by('-order_count')[:10]
    
    # Top meals
    top_meals = Meal.objects.annotate(
        order_count=Count('orders')
    ).order_by('-order_count')[:10]
    
    context = {
        'daily_revenue': daily_revenue,
        'daily_orders': daily_orders,
        'top_cooks': top_cooks,
        'top_meals': top_meals,
    }
    return render(request, 'admin_panel/analytics.html', context)

