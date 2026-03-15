from django.db import models
from apps.accounts.models import User, CookProfile
from apps.buyers.models import BuyerOrder


class Report(models.Model):
    REASON_CHOICES = [
        ('food_quality_issue', 'Food quality issue'),
        ('cook_did_not_prepare', 'Cook did not prepare order'),
        ('cook_not_responding', 'Cook not responding'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('resolved', 'Resolved'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    cook = models.ForeignKey(CookProfile, on_delete=models.CASCADE, related_name='reports_received')
    order = models.ForeignKey(BuyerOrder, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.id} on Order #{self.order_id}"
