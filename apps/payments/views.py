from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Payment
from apps.buyers.models import BuyerOrder


@login_required
def process_payment(request, order_id):
    """Process Razorpay payment"""
    order = get_object_or_404(BuyerOrder, pk=order_id, buyer=request.user)
    
    if order.payment_method != 'online':
        messages.error(request, 'This order is not for online payment.')
        return redirect('buyers:order_detail', pk=order_id)
    
    # Initialize Razorpay client (import lazily to avoid hard dependency at module import)
    try:
        import razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    except Exception:
        client = None
    
    # Create Razorpay order
    razorpay_order = client.order.create({
        'amount': int(order.total_amount * 100),  # Amount in paise
        'currency': 'INR',
        'receipt': f'order_{order.id}',
    })
    
    # Create payment record
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'razorpay_order_id': razorpay_order['id'],
            'amount': order.total_amount,
            'status': 'pending',
            'method': 'razorpay'
        }
    )
    
    if not created:
        payment.razorpay_order_id = razorpay_order['id']
        payment.save()
    
    context = {
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': order.total_amount,
        'callback_url': request.build_absolute_uri('/payments/callback/'),
    }
    return render(request, 'payments/process.html', context)


@login_required
def payment_success(request):
    """Payment success page"""
    return render(request, 'payments/success.html')


@login_required
def payment_failure(request):
    """Payment failure page"""
    return render(request, 'payments/failure.html')


@csrf_exempt
def payment_callback(request):
    """Razorpay payment callback"""
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            
            # Verify signature
            try:
                import razorpay
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            except Exception:
                client = None
            params = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            try:
                client.utility.verify_payment_signature(params)
                # Payment successful
                payment.razorpay_payment_id = razorpay_payment_id
                payment.razorpay_signature = razorpay_signature
                payment.status = 'success'
                payment.save()
                
                # Update cook order payment status
                from apps.cooks.models import CookOrder
                cook_order = CookOrder.objects.filter(
                    buyer=payment.order.buyer,
                    meal=payment.order.meal,
                    pickup_slot=payment.order.pickup_slot
                ).first()
                if cook_order:
                    cook_order.payment_status = 'paid'
                    cook_order.save()
                
                return redirect('payments:success')
            except razorpay.errors.SignatureVerificationError:
                # Payment verification failed
                payment.status = 'failed'
                payment.save()
                return redirect('payments:failure')
        except Payment.DoesNotExist:
            return redirect('payments:failure')
    
    return redirect('payments:failure')

