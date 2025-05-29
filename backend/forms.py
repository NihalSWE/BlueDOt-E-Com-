from django import forms
from .models import *
from django.forms.models import inlineformset_factory


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
        
        
class AboutUsAboutAreaForm(forms.ModelForm):
    class Meta:
        model = AboutUs_AboutArea
        fields = '__all__'

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'quality_description': forms.Textarea(attrs={'rows': 3}),
            'automation_description': forms.Textarea(attrs={'rows': 3}),
        }

class CallToActionForm(forms.ModelForm):
    class Meta:
        model = CallToAction
        fields = ['sub_title', 'main_title', 'button_text', 'button_link', 'shape1']
        widgets = {
            'sub_title': forms.TextInput(attrs={'class': 'form-control'}),
            'main_title': forms.TextInput(attrs={'class': 'form-control'}),
            'button_text': forms.TextInput(attrs={'class': 'form-control'}),
            'button_link': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '/contact/'}),
        }
        
        

class ChooseUsSectionForm(forms.ModelForm):
    class Meta:
        model = ChooseUsSection
        fields = ['thumb_image', 'shape_3', 'shape_4']
        widgets = {
             'thumb_image': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
            'shape_3': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
            'shape_4': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
        }

class ChooseUsItemForm(forms.ModelForm):
    class Meta:
        model = ChooseUsItem
        fields = ['icon_image', 'title', 'description']
        widgets = {
            'icon_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        

class FAQSectionForm(forms.ModelForm):
    class Meta:
        model = FAQSection
        fields = '__all__'
        widgets = {
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'section_title': forms.TextInput(attrs={'class': 'form-control'}),
            'section_subtitle': forms.TextInput(attrs={'class': 'form-control'}),
        }

FAQItemFormSet = inlineformset_factory(
    FAQSection,
    FAQItem,
    fields=['question', 'answer', 'is_expanded'],
    extra=1,
    widgets={
        'question': forms.TextInput(attrs={'class': 'form-control'}),
        'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
    }
)