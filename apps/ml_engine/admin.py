from django.contrib import admin
from .models import RecommendationCache, DemandForecast


@admin.register(RecommendationCache)
class RecommendationCacheAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp')
    filter_horizontal = ('recommended_meals',)


@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):
    list_display = ('meal', 'date', 'predicted_demand', 'confidence', 'created_at')
    list_filter = ('date', 'created_at')








