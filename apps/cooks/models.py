from django.db import models
from apps.accounts.models import User, CookProfile


class Meal(models.Model):
    """Meal listing model"""
    MEAL_CATEGORY = [
        ('regular', 'Regular Meal'),
        ('healthy', 'Healthy/Salad'),
        ('special', 'Special Dish'),
    ]
    
    cook = models.ForeignKey(CookProfile, on_delete=models.CASCADE, related_name='meals')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    ingredients = models.TextField(help_text="List of ingredients")
    meal_category = models.CharField(max_length=20, choices=MEAL_CATEGORY, default='regular', help_text="Categorize as healthy/salad for health-focused meals")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} by {self.cook.user.username}"


class MealImage(models.Model):
    """Multiple images for a meal"""
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='meal_images/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
    
    def __str__(self):
        return f"Image for {self.meal.name}"


class PickupSlot(models.Model):
    """Pickup time slots for meals"""
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='pickup_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_quantity = models.IntegerField(default=10)
    available_quantity = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['meal', 'date', 'start_time']
    
    def __str__(self):
        return f"{self.meal.name} - {self.date} {self.start_time} to {self.end_time}"


class CookOrder(models.Model):
    """Orders received by cooks"""
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='placed_orders')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='orders')
    pickup_slot = models.ForeignKey(PickupSlot, on_delete=models.CASCADE, related_name='orders')
    quantity = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.meal.name} by {self.buyer.username}"
    
    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = self.meal.price * self.quantity
        super().save(*args, **kwargs)


class CookReview(models.Model):
    """Reviews for cooks/meals"""
    order = models.OneToOneField(CookOrder, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.order.meal.name} - {self.rating} stars"


class CookAnalytics(models.Model):
    """Daily analytics for cooks"""
    cook = models.ForeignKey(CookProfile, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    orders_count = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cook', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.cook.user.username} on {self.date}"


class HealthyDiet(models.Model):
    """Healthy diet section featuring salads and health-focused meals"""
    meal = models.OneToOneField(Meal, on_delete=models.CASCADE, related_name='healthy_diet')
    dietary_tags = models.JSONField(default=list, blank=True, help_text='Tags like ["vegan", "low-calorie", "gluten-free"]')
    featured = models.BooleanField(default=False, help_text='Display in featured healthy diets section')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-featured', '-created_at']
        verbose_name_plural = 'Healthy Diets'
    
    def __str__(self):
        return f"Healthy: {self.meal.name}"






