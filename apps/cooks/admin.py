from django.contrib import admin
from apps.accounts.models import CookProfile
# CookProfile admin for FSSAI verification
@admin.register(CookProfile)
class CookProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'fssai_number', 'updated_at', 'fssai_certificate_thumbnail'
    )
    list_filter = ('updated_at',)
    search_fields = ('user__username', 'fssai_number')
    readonly_fields = ()



    def fssai_certificate_thumbnail(self, obj):
        if obj.fssai_certificate:
            return f'<img src="{obj.fssai_certificate.url}" width="80" height="80" style="object-fit:cover;" />'
        return '-'
    fssai_certificate_thumbnail.allow_tags = True
    fssai_certificate_thumbnail.short_description = 'Certificate'



from .models import Meal, MealImage, PickupSlot, CookOrder, CookReview, CookAnalytics, HealthyDiet

@admin.register(HealthyDiet)
class HealthyDietAdmin(admin.ModelAdmin):
    list_display = ('meal', 'featured', 'created_at')
    list_filter = ('featured', 'created_at')
    search_fields = ('meal__name',)


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'cook', 'price', 'is_available', 'created_at')
    list_filter = ('is_available', 'created_at')
    search_fields = ('name', 'cook__user__username')


@admin.register(MealImage)
class MealImageAdmin(admin.ModelAdmin):
    list_display = ('meal', 'is_primary', 'created_at')
    list_filter = ('is_primary',)


@admin.register(PickupSlot)
class PickupSlotAdmin(admin.ModelAdmin):
    list_display = ('meal', 'date', 'start_time', 'end_time', 'available_quantity', 'is_active')
    list_filter = ('date', 'is_active')


@admin.register(CookOrder)
class CookOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'meal', 'quantity', 'total_amount', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('buyer__username', 'meal__name')


@admin.register(CookReview)
class CookReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'rating', 'sentiment_score', 'created_at')
    list_filter = ('rating', 'created_at')


@admin.register(CookAnalytics)
class CookAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('cook', 'date', 'orders_count', 'revenue')
    list_filter = ('date',)






