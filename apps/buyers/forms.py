from django import forms
from .models import BuyerReview


class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for meals...'
        })
    )
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter location...',
            'id': 'location-input'
        })
    )


class BuyerReviewForm(forms.ModelForm):
    class Meta:
        model = BuyerReview
        fields = ['overall_rating', 'freshness_rating', 'hygiene_rating', 'taste_rating', 
                  'packaging_rating', 'comment', 'food_photo']
        widgets = {
            'overall_rating': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'required': 'required'
            }),
            'freshness_rating': forms.Select(attrs={'class': 'form-select'}),
            'hygiene_rating': forms.Select(attrs={'class': 'form-select'}),
            'taste_rating': forms.Select(attrs={'class': 'form-select'}),
            'packaging_rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Share your detailed feedback about the meal, packaging, pickup experience, and any suggestions for improvement...',
                'maxlength': '1000'
            }),
            'food_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'food-photo-upload'
            }),
        }
        labels = {
            'overall_rating': 'Overall Rating (Required)',
            'freshness_rating': 'Freshness Rating',
            'hygiene_rating': 'Hygiene Rating',
            'taste_rating': 'Taste Rating',
            'packaging_rating': 'Packaging Rating',
            'comment': 'Additional Comments',
            'food_photo': 'Upload Food Photo (Optional)',
        }
    
    def clean(self):
        """Custom validation for the review form"""
        cleaned_data = super().clean()
        overall_rating = cleaned_data.get('overall_rating')
        
        # Overall rating is required
        if not overall_rating:
            raise forms.ValidationError(
                'Overall rating is required. Please select a rating.'
            )
        
        # Comment validation - optional but encourage at least 10 characters if provided
        comment = cleaned_data.get('comment', '').strip()
        if comment and len(comment) < 10:
            raise forms.ValidationError(
                'Please provide at least 10 characters in your comment.'
            )
        
        # Food photo validation
        food_photo = cleaned_data.get('food_photo')
        if food_photo:
            # Check file size (max 5MB)
            if food_photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    'Photo file size must be less than 5MB.'
                )
            # Check file extension
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            file_ext = food_photo.name.split('.')[-1].lower()
            if file_ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Invalid image format. Allowed formats: {", ".join(valid_extensions)}'
                )
        
        return cleaned_data






