import requests
from django.conf import settings


class MSG91Service:
    """MSG91 SMS and WhatsApp notification service"""
    
    def __init__(self):
        self.auth_key = settings.MSG91_AUTH_KEY
        self.sender_id = settings.MSG91_SENDER_ID
        self.base_url = "https://api.msg91.com/api/v5"
    
    def send_sms(self, mobile, message):
        """Send SMS via MSG91"""
        if not self.auth_key or not self.sender_id:
            return False
        
        url = f"{self.base_url}/flow"
        headers = {
            "authkey": self.auth_key,
            "Content-Type": "application/json"
        }
        payload = {
            "template_id": "your_template_id",  # Replace with actual template ID
            "sender": self.sender_id,
            "short_url": "0",
            "mobiles": mobile,
            "message": message
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"MSG91 SMS Error: {e}")
            return False
    
    def send_whatsapp(self, mobile, message):
        """Send WhatsApp message via MSG91"""
        if not self.auth_key:
            return False
        
        url = f"{self.base_url}/whatsapp/send"
        headers = {
            "authkey": self.auth_key,
            "Content-Type": "application/json"
        }
        payload = {
            "template_id": "your_template_id",  # Replace with actual template ID
            "sender": self.sender_id,
            "short_url": "0",
            "mobiles": mobile,
            "message": message
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"MSG91 WhatsApp Error: {e}")
            return False


class NotificationService:
    """Notification service for order updates"""
    
    def __init__(self):
        self.msg91 = MSG91Service()
    
    def send_order_confirmation(self, order):
        """Send order confirmation notification"""
        message = f"Your order #{order.id} for {order.meal.name} has been confirmed. Pickup: {order.pickup_slot.date} at {order.pickup_slot.start_time}"
        mobile = order.buyer.phone_number
        if mobile:
            self.msg91.send_sms(mobile, message)
            # self.msg91.send_whatsapp(mobile, message)  # Uncomment if WhatsApp is enabled
    
    def send_order_status_update(self, order, status):
        """Send order status update notification"""
        message = f"Your order #{order.id} status has been updated to: {status}"
        mobile = order.buyer.phone_number
        if mobile:
            self.msg91.send_sms(mobile, message)
    
    def send_pickup_reminder(self, order):
        """Send pickup reminder"""
        message = f"Reminder: Your order #{order.id} is ready for pickup today at {order.pickup_slot.start_time}"
        mobile = order.buyer.phone_number
        if mobile:
            self.msg91.send_sms(mobile, message)
    
    def send_payment_confirmation(self, payment):
        """Send payment confirmation"""
        message = f"Payment of ₹{payment.amount} for order #{payment.order.id} has been confirmed. Thank you!"
        mobile = payment.order.buyer.phone_number
        if mobile:
            self.msg91.send_sms(mobile, message)






