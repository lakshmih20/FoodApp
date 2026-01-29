from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile, CookProfile


class UserRegistrationForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial='buyer'
    )
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=17, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'user_type', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'city', 'state', 'pincode', 'latitude', 'longitude', 
                  'dietary_preferences', 'profile_image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'dietary_preferences': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CookProfileForm(forms.ModelForm):
    class Meta:
        model = CookProfile
        fields = ['bio', 'address', 'city', 'state', 'pincode', 'latitude', 'longitude', 
                  'profile_image', 'fssai_certificate', 'fssai_certificate_number']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'fssai_certificate': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'fssai_certificate_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FSSAI Registration Number'}),
        }


class CookRegistrationForm(forms.ModelForm):
    """
    Cook registration form with required address/location fields.
    This ensures every cook has location data for location-based meal discovery.
    """
    class Meta:
        model = CookProfile
        fields = ['bio', 'address', 'city', 'state', 'pincode', 'profile_image', 'fssai_certificate', 'fssai_certificate_number']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': True}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'fssai_certificate': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'fssai_certificate_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FSSAI Registration Number'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].required = True
        self.fields['city'].required = True
        self.fields['state'].required = True
        self.fields['pincode'].required = True






