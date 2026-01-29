from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BuyerOrder
from apps.cooks.models import CookOrder


@receiver(post_save, sender=BuyerOrder)
def sync_cook_order_status(sender, instance, **kwargs):
    """Sync BuyerOrder status to CookOrder"""
    try:
        cook_order = CookOrder.objects.filter(
            buyer=instance.buyer,
            meal=instance.meal,
            pickup_slot=instance.pickup_slot,
            created_at__date=instance.created_at.date()
        ).first()
        
        if cook_order and cook_order.status != instance.status:
            cook_order.status = instance.status
            cook_order.save(update_fields=['status'])
    except CookOrder.DoesNotExist:
        pass






