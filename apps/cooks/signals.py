from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CookOrder
from apps.buyers.models import BuyerOrder


@receiver(post_save, sender=CookOrder)
def sync_buyer_order_status(sender, instance, **kwargs):
    """Sync CookOrder status to BuyerOrder"""
    try:
        buyer_order = BuyerOrder.objects.filter(
            buyer=instance.buyer,
            meal=instance.meal,
            pickup_slot=instance.pickup_slot,
            created_at__date=instance.created_at.date()
        ).first()
        
        if buyer_order and buyer_order.status != instance.status:
            buyer_order.status = instance.status
            buyer_order.save(update_fields=['status'])
    except BuyerOrder.DoesNotExist:
        pass






