from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from apps.accounts.models import User, CookProfile
from apps.cooks.models import Meal
from apps.buyers.models import BuyerOrder
from apps.payments.models import Payment
from apps.notifications.models import Notification
from .models import Report


def _require_staff(request):
    if not request.user.is_staff:
        return redirect('buyers:home')
    return None


@login_required
def dashboard(request):
    blocked = _require_staff(request)
    if blocked:
        return blocked

    today = timezone.now().date()
    total_users = User.objects.filter(user_type='buyer').count()
    total_cooks = CookProfile.objects.count()
    verified_cooks = CookProfile.objects.filter(is_verified=True).count()
    pending_verifications = CookProfile.objects.filter(verification_status='pending').count()
    today_orders = BuyerOrder.objects.filter(created_at__date=today).count()
    active_meals = Meal.objects.filter(is_available=True).count()
    today_revenue = Payment.objects.filter(created_at__date=today, status='success').aggregate(
        total=Sum('amount')
    )['total'] or 0

    recent_orders = BuyerOrder.objects.select_related('buyer', 'cook__user').order_by('-created_at')[:10]
    pending_cooks = CookProfile.objects.select_related('user').filter(verification_status='pending').order_by('-created_at')[:10]

    context = {
        'total_users': total_users,
        'total_cooks': total_cooks,
        'verified_cooks': verified_cooks,
        'pending_verifications': pending_verifications,
        'today_orders': today_orders,
        'active_meals': active_meals,
        'today_revenue': today_revenue,
        'recent_orders': recent_orders,
        'pending_cooks': pending_cooks,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
def cook_verification_list(request):
    blocked = _require_staff(request)
    if blocked:
        return blocked
    pending_cooks = CookProfile.objects.select_related('user').filter(verification_status='pending').order_by('-created_at')
    return render(request, 'admin_panel/cook_verification_list.html', {'pending_cooks': pending_cooks})


@login_required
def cook_verification_review(request, cook_id):
    blocked = _require_staff(request)
    if blocked:
        return blocked
    cook = get_object_or_404(CookProfile.objects.select_related('user'), pk=cook_id)
    return render(request, 'admin_panel/cook_review.html', {'cook': cook})


@login_required
def verify_cook(request, cook_id):
    blocked = _require_staff(request)
    if blocked:
        return blocked
    if request.method != 'POST':
        messages.info(request, 'Please review the FSSAI certificate before approving.')
        return redirect('admin_panel:cook_verification_review', cook_id=cook_id)

    cook = get_object_or_404(CookProfile, pk=cook_id)
    if not cook.fssai_certificate:
        messages.error(request, 'Cannot verify cook without an uploaded FSSAI certificate.')
        return redirect('admin_panel:cook_verification_review', cook_id=cook_id)

    cook.is_verified = True
    cook.verification_status = 'verified'
    cook.fssai_certificate_status = 'approved'
    cook.certificate_verification_date = timezone.now()
    cook.certificate_rejection_reason = ''
    cook.save(update_fields=[
        'is_verified',
        'verification_status',
        'fssai_certificate_status',
        'certificate_verification_date',
        'certificate_rejection_reason',
    ])
    Notification.objects.create(
        user=cook.user,
        message='Congratulations! Your profile has been verified. You can now publish meals.'
    )
    messages.success(request, f'{cook.user.username} verified.')
    next_url = request.POST.get('next')
    return redirect(next_url or 'admin_panel:cook_verification_list')


@login_required
def reject_cook(request, cook_id):
    blocked = _require_staff(request)
    if blocked:
        return blocked
    if request.method != 'POST':
        messages.info(request, 'Please review the FSSAI certificate before rejecting.')
        return redirect('admin_panel:cook_verification_review', cook_id=cook_id)

    cook = get_object_or_404(CookProfile, pk=cook_id)
    cook.is_verified = False
    cook.verification_status = 'rejected'
    cook.fssai_certificate_status = 'rejected'
    cook.certificate_verification_date = timezone.now()
    cook.certificate_rejection_reason = request.POST.get('rejection_reason', '').strip()
    cook.save(update_fields=[
        'is_verified',
        'verification_status',
        'fssai_certificate_status',
        'certificate_verification_date',
        'certificate_rejection_reason',
    ])
    Notification.objects.create(
        user=cook.user,
        message='Your FSSAI certificate was rejected. Please upload a valid certificate and resubmit for verification.'
    )
    messages.warning(request, f'{cook.user.username} rejected.')
    next_url = request.POST.get('next')
    return redirect(next_url or 'admin_panel:cook_verification_list')


@login_required
def user_list(request):
    blocked = _require_staff(request)
    if blocked:
        return blocked

    buyers = User.objects.filter(user_type='buyer').annotate(total_orders=Count('buyer_orders')).order_by('-date_joined')
    cooks = User.objects.filter(user_type='cook').annotate(total_meals=Count('cook_profile__meals')).order_by('-date_joined')
    tab = request.GET.get('tab', 'buyers')
    return render(request, 'admin_panel/user_list.html', {
        'buyers': buyers,
        'cooks': cooks,
        'tab': tab,
    })


@login_required
def toggle_user_active(request, user_id):
    blocked = _require_staff(request)
    if blocked:
        return blocked
    user = get_object_or_404(User, pk=user_id)
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    messages.success(request, f'User {user.username} is now {"active" if user.is_active else "inactive"}.')
    return redirect('admin_panel:user_list')


@login_required
def order_list(request):
    blocked = _require_staff(request)
    if blocked:
        return blocked
    status_filter = request.GET.get('status', '').strip()
    query = request.GET.get('q', '').strip()
    orders = BuyerOrder.objects.select_related('buyer', 'cook__user', 'meal').order_by('-created_at')

    if status_filter:
        if status_filter == 'collected':
            orders = orders.filter(status='completed')
        else:
            orders = orders.filter(status=status_filter)

    if query:
        if query.isdigit():
            orders = orders.filter(Q(id=int(query)) | Q(buyer__username__icontains=query))
        else:
            orders = orders.filter(buyer__username__icontains=query)

    return render(request, 'admin_panel/order_list.html', {
        'orders': orders,
        'status_filter': status_filter,
        'query': query,
    })


@login_required
def dispute_list(request):
    blocked = _require_staff(request)
    if blocked:
        return blocked
    reports = Report.objects.select_related('buyer', 'cook__user', 'order').order_by('-created_at')
    return render(request, 'admin_panel/dispute_list.html', {'reports': reports})


@login_required
def resolve_dispute(request, report_id):
    blocked = _require_staff(request)
    if blocked:
        return blocked
    report = get_object_or_404(Report, pk=report_id)
    if request.method == 'POST':
        report.status = 'resolved'
        report.admin_note = request.POST.get('admin_note', '').strip()
        report.save(update_fields=['status', 'admin_note', 'updated_at'])
        messages.success(request, f'Report #{report.id} resolved.')
    return redirect('admin_panel:dispute_list')


@login_required
def meal_list(request):
    blocked = _require_staff(request)
    if blocked:
        return blocked
    meals = Meal.objects.select_related('cook__user').prefetch_related('images').order_by('-created_at')
    return render(request, 'admin_panel/meal_list.html', {'meals': meals})


@login_required
def toggle_meal_publish(request, meal_id):
    blocked = _require_staff(request)
    if blocked:
        return blocked
    meal = get_object_or_404(Meal, pk=meal_id)
    meal.is_available = not meal.is_available
    meal.save(update_fields=['is_available'])
    if meal.is_available:
        msg = f'Your meal {meal.name} is live again.'
        messages.success(request, f'{meal.name} republished.')
    else:
        msg = f'Your meal {meal.name} has been unpublished by admin due to compliance issues. Please contact support for more information.'
        messages.warning(request, f'{meal.name} unpublished.')
    Notification.objects.create(user=meal.cook.user, message=msg)
    return redirect('admin_panel:meal_list')

