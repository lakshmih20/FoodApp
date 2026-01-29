from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Custom User model extending AbstractUser"""
    USER_TYPE_CHOICES = [
        ('buyer', 'Buyer'),
        ('cook', 'Cook'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """User profile for buyers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    dietary_preferences = models.JSONField(default=list, blank=True)  # ['vegetarian', 'vegan', etc.]
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class CookProfile(models.Model):
    """Cook profile for home cooks"""
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    CERTIFICATE_STATUS = [
        ('not_submitted', 'Not Submitted'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cook_profile')
    bio = models.TextField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # Whether the cook is currently available to accept new pickup orders
    is_available_now = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    # FSSAI Certificate fields
    fssai_certificate = models.ImageField(upload_to='fssai_certificates/', blank=True, null=True, help_text='Upload FSSAI certificate sample')
    fssai_certificate_status = models.CharField(max_length=20, choices=CERTIFICATE_STATUS, default='not_submitted')
    fssai_certificate_number = models.CharField(max_length=100, blank=True, help_text='FSSAI registration number')
    certificate_verification_date = models.DateTimeField(null=True, blank=True)
    certificate_rejection_reason = models.TextField(blank=True, help_text='Reason for certificate rejection if applicable')
    documents = models.JSONField(default=list, blank=True)  # Store verification documents

    # AI-assisted FSSAI verification fields
    fssai_number = models.CharField(max_length=20, blank=True, help_text='FSSAI number entered by cook')
    fssai_expiry_date = models.DateField(null=True, blank=True, help_text='Expiry date entered by cook')
    # Removed OCR/risk/status fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Cook Profile"
    
    def is_verified(self):
        return self.verification_status == 'approved'






