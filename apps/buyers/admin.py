from django.contrib import admin
from .models import BuyerOrder, BuyerReview, FavoriteCook, SearchHistory


@admin.register(BuyerOrder)
class BuyerOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'meal', 'cook', 'quantity', 'total_amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('buyer__username', 'meal__name', 'cook__user__username')


@admin.register(BuyerReview)
class BuyerReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'overall_rating', 'sentiment_score', 'created_at')
    list_filter = ('overall_rating', 'created_at')


@admin.register(FavoriteCook)
class FavoriteCookAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'cook', 'created_at')
    list_filter = ('created_at',)


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'query', 'location', 'timestamp')
    list_filter = ('timestamp',)






