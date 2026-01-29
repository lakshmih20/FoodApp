from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'status', 'method', 'created_at')
    list_filter = ('status', 'method', 'created_at')
    search_fields = ('order__id', 'razorpay_order_id', 'razorpay_payment_id')






