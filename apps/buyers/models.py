from django.db import models
from apps.accounts.models import User, CookProfile
from apps.cooks.models import Meal, PickupSlot


class BuyerOrder(models.Model):
    """Orders placed by buyers"""
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD = [
        ('online', 'Online Payment'),
        ('cash', 'Cash on Pickup'),
    ]
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_orders')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='buyer_orders')
    cook = models.ForeignKey(CookProfile, on_delete=models.CASCADE, related_name='buyer_orders')
    pickup_slot = models.ForeignKey(PickupSlot, on_delete=models.CASCADE, related_name='buyer_orders')
    quantity = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='cash')
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.meal.name} by {self.buyer.username}"


class BuyerReview(models.Model):
    """Reviews by buyers with questionnaire and food photos"""
    FRESHNESS_CHOICES = [
        (1, 'Poor - Stale/Old'),
        (2, 'Fair - Slightly stale'),
        (3, 'Good - Fresh'),
        (4, 'Very Good - Very Fresh'),
        (5, 'Excellent - Extremely Fresh'),
    ]
    
    HYGIENE_CHOICES = [
        (1, 'Poor - Very unsanitary'),
        (2, 'Fair - Some hygiene concerns'),
        (3, 'Good - Generally hygienic'),
        (4, 'Very Good - Very clean'),
        (5, 'Excellent - Impeccably clean'),
    ]
    
    TASTE_CHOICES = [
        (1, 'Poor - Inedible'),
        (2, 'Fair - Barely edible'),
        (3, 'Good - Acceptable taste'),
        (4, 'Very Good - Delicious'),
        (5, 'Excellent - Exceptional taste'),
    ]
    
    PACKAGING_CHOICES = [
        (1, 'Poor - Damaged/leaking'),
        (2, 'Fair - Some issues'),
        (3, 'Good - Adequate packaging'),
        (4, 'Very Good - Well packaged'),
        (5, 'Excellent - Premium packaging'),
    ]
    
    order = models.OneToOneField(BuyerOrder, on_delete=models.CASCADE, related_name='buyer_review')
    overall_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    
    # Questionnaire-based review fields
    freshness_rating = models.IntegerField(choices=FRESHNESS_CHOICES, null=True, blank=True)
    hygiene_rating = models.IntegerField(choices=HYGIENE_CHOICES, null=True, blank=True)
    taste_rating = models.IntegerField(choices=TASTE_CHOICES, null=True, blank=True)
    packaging_rating = models.IntegerField(choices=PACKAGING_CHOICES, null=True, blank=True)
    
    # Food photo
    food_photo = models.ImageField(upload_to='review_food_photos/', blank=True, null=True)
    
    # Sentiment analysis
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for Order #{self.order.id} - {self.overall_rating} stars"


class FavoriteCook(models.Model):
    """Favorite cooks for buyers"""
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_cooks')
    cook = models.ForeignKey(CookProfile, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['buyer', 'cook']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.buyer.username} favorites {self.cook.user.username}"


class SearchHistory(models.Model):
    """Search history for buyers"""
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Search by {self.buyer.username} at {self.timestamp}"






