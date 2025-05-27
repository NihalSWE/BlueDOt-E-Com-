from django import forms
from .models import *

class HomeSliderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add modern styling classes to all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control modern-input',
                'autocomplete': 'off'
            })
        
        # Specific field customizations
        self.fields['title'].widget.attrs.update({
            'placeholder': 'Enter slide title (e.g., Quality Printing Services)',
        })
        
        self.fields['subtitle'].widget.attrs.update({
            'placeholder': 'Optional subtitle text',
            'class': 'form-control modern-input subtitle-field'
        })
        
        self.fields['button_text'].widget.attrs.update({
            'placeholder': 'Call-to-action text (e.g., Get Started)'
        })
        
        self.fields['button_link'].widget.attrs.update({
            'placeholder': 'URL path (e.g., /contact or #services)'
        })
        
        self.fields['image'].widget.attrs.update({
            'class': 'form-control modern-file-input',
            'accept': 'image/*'
        })

    class Meta:
        model = HomeSlider
        fields = '__all__'

    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        if image:
            if image.size > 5*1024*1024:  # 5MB limit
                raise forms.ValidationError("Image file too large ( > 5MB )")
            return image
        return image
    
    
    

# Contac banner form
class ContactUsBannerForm(forms.ModelForm):
    class Meta:
        model = ContactUsBanner
        fields = ['title', 'subtitle', 'background_image']
        
# contact page branch locations

class ContactLocationForm(forms.ModelForm):
    class Meta:
        model = ContactLocation
        fields = ['city', 'address', 'image']
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        # Add any image validation here if needed
        return image
    
    
class AboutUsBannerForm(forms.ModelForm):
    class Meta:
        model = AboutUsBanner
        fields = ['title', 'subtitle', 'background_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitle': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'background_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
