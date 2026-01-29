from django import forms
from .models import Meal, PickupSlot
from apps.accounts.models import CookProfile
class CookFSSAICertificateForm(forms.ModelForm):
    class Meta:
        model = CookProfile
        fields = [
            'fssai_certificate',
            'fssai_number',
            'fssai_expiry_date',
        ]
        widgets = {
            'fssai_certificate': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'fssai_number': forms.TextInput(attrs={'class': 'form-control'}),
            'fssai_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['name', 'description', 'price', 'ingredients', 'meal_category', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ingredients': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'meal_category': forms.Select(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MealImageForm(forms.Form):
    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=False
    )


class PickupSlotForm(forms.ModelForm):
    class Meta:
        model = PickupSlot
        fields = ['date', 'start_time', 'end_time', 'max_quantity', 'is_active']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'max_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }






