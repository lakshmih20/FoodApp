from django.db import models
from apps.accounts.models import User
from apps.cooks.models import Meal


class RecommendationCache(models.Model):
    """Cached recommendations for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recommendation_cache')
    recommended_meals = models.ManyToManyField(Meal, related_name='recommended_to')
    timestamp = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Recommendations for {self.user.username}"


class DemandForecast(models.Model):
    """Demand forecasts for meals"""
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='forecasts')
    date = models.DateField()
    predicted_demand = models.IntegerField()
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['meal', 'date']
        ordering = ['date']
    
    def __str__(self):
        return f"Forecast for {self.meal.name} on {self.date}"








