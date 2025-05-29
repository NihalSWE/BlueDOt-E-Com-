from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms import modelformset_factory
# Create your views here.


def deshboard(request):
    return render(request, 'backend/index.html')

def home(request):
    # Get all sliders ordered by creation date (newest first)
    sliders = HomeSlider.objects.all().order_by('-created_at')
    
    # Handle form submissions (for admin functionality)
    if request.method == "POST":
        # Edit existing slider
        if 'edit_id' in request.POST:
            try:
                slider = get_object_or_404(HomeSlider, id=request.POST['edit_id'])
                form = HomeSliderForm(request.POST, request.FILES, instance=slider)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Slider updated successfully!")
                else:
                    messages.error(request, "Error updating slider. Please check the form.")
            except Exception as e:
                messages.error(request, f"Error updating slider: {str(e)}")
        
        # Delete slider
        elif 'delete_id' in request.POST:
            try:
                slider = get_object_or_404(HomeSlider, id=request.POST['delete_id'])
                slider.delete()
                messages.success(request, "Slider deleted successfully!")
            except Exception as e:
                messages.error(request, f"Error deleting slider: {str(e)}")
        
        # Create new slider
        else:
            form = HomeSliderForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "New slider added successfully!")
            else:
                messages.error(request, "Error adding new slider. Please check the form.")
        
        return redirect('home')
    
    # For GET requests or if no form submission
    form = HomeSliderForm()
    
    context = {
        'sliders': sliders,
        'form': form,
    }
    
    return render(request, 'backend/home.html', context)


def aboutUs_banner(request):
    banner = AboutUsBanner.objects.last()
    if not banner:
        banner = AboutUsBanner.objects.create()

    if request.method == 'POST':
        form = AboutUsBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'About Us banner updated successfully!')
            return redirect('aboutUs_banner')
    else:
        form = AboutUsBannerForm(instance=banner)

    return render(request, 'backend/aboutUs_banner.html', {
        'form': form,
        'banner': banner
    })
    
def aboutUs_aboutarea(request):
    about = AboutUs_AboutArea.objects.first()
    form = AboutUsAboutAreaForm(request.POST or None, request.FILES or None, instance=about)

    if request.method == 'POST' and form.is_valid():
        form.save()

    image_fields = ['bg_image', 'man_image', 'shape1', 'shape2', 'call_image']
    image_previews = {field: getattr(about, field).url if getattr(about, field) else None for field in image_fields} if about else {}

    return render(request, 'backend/aboutUs_aboutarea.html', {
        'form': form,
        'about': about,
        'image_previews': image_previews,
    })



def aboutUs_callToaction(request):
    cta = CallToAction.objects.first()

    if request.method == "POST":
        form = CallToActionForm(request.POST, request.FILES, instance=cta)
        if form.is_valid():
            form.save()
            return redirect('aboutUs_callToaction')
    else:
        form = CallToActionForm(instance=cta)

    return render(request, 'backend/aboutUs_callToaction.html', {
        'form': form,
        'cta': cta,
    })

from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .models import ChooseUsSection, ChooseUsItem
from .forms import ChooseUsSectionForm, ChooseUsItemForm

def aboutUs_chooseUs(request):
    section = ChooseUsSection.objects.last()

    # If no section exists, create one (optional)
    if not section:
        section = ChooseUsSection.objects.create()

    # Form for section images
    section_form = ChooseUsSectionForm(request.POST or None, request.FILES or None, instance=section)

    # Formset for items (extra=0 means no empty forms by default)
    ChooseUsItemFormSet = modelformset_factory(ChooseUsItem, form=ChooseUsItemForm, can_delete=True, extra=0)
    queryset = ChooseUsItem.objects.filter(section=section)
    formset = ChooseUsItemFormSet(request.POST or None, request.FILES or None, queryset=queryset)

    if request.method == 'POST':
        if 'save_section' in request.POST:
            # Saving section form only
            if section_form.is_valid():
                section_form.save()
                return redirect('aboutUs_chooseUs')

        elif 'save_items' in request.POST:
            # Saving formset for items
            if formset.is_valid():
                instances = formset.save(commit=False)
                # Save new or changed items
                for obj in instances:
                    obj.section = section
                    obj.save()
                # Delete items marked for deletion
                for obj in formset.deleted_objects:
                    obj.delete()
                return redirect('aboutUs_chooseUs')

        elif 'add_item' in request.POST:
            # Adding new item from modal form
            add_item_form = ChooseUsItemForm(request.POST, request.FILES)
            if add_item_form.is_valid():
                new_item = add_item_form.save(commit=False)
                new_item.section = section
                new_item.save()
                return redirect('aboutUs_chooseUs')
    else:
        add_item_form = ChooseUsItemForm()

    context = {
        'section_form': section_form,
        'formset': formset,
        'add_item_form': add_item_form,
        'section': section,
    }
    return render(request, 'backend/aboutUs_chooseUs.html', context)


def aboutus_faq(request):
    faq_section = FAQSection.objects.first()

    if request.method == 'POST':
        form = FAQSectionForm(request.POST, request.FILES, instance=faq_section)
        formset = FAQItemFormSet(request.POST, instance=faq_section)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('aboutus_faq')  # Adjust this to your named URL
    else:
        form = FAQSectionForm(instance=faq_section)
        formset = FAQItemFormSet(instance=faq_section)

    return render(request, 'backend/aboutUs_faq.html', {
        'form': form,
        'formset': formset,
    })





def contactUs(request):
    banner = ContactUsBanner.objects.last()  # Get the most recently added banner

    if not banner:
        banner = ContactUsBanner.objects.create()  # Create one if none exists

    if request.method == 'POST':
        form = ContactUsBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            return redirect('contactUs')
    else:
        form = ContactUsBannerForm(instance=banner)

    return render(request, 'backend/contactus.html', {'form': form, 'banner': banner})

def contactUs_location(request):
    locations = ContactLocation.objects.all()

    # Handle AJAX POST requests for add/edit/delete
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        action = request.POST.get('action')

        if action == "add":
            form = ContactLocationForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return JsonResponse({"success": True, "message": "Location added successfully."})
            else:
                return JsonResponse({"success": False, "errors": form.errors})

        elif action == "edit":
            loc_id = request.POST.get('id')
            location = get_object_or_404(ContactLocation, id=loc_id)
            form = ContactLocationForm(request.POST, request.FILES, instance=location)
            if form.is_valid():
                form.save()
                return JsonResponse({"success": True, "message": "Location updated successfully."})
            else:
                return JsonResponse({"success": False, "errors": form.errors})

        elif action == "delete":
            loc_id = request.POST.get('id')
            location = get_object_or_404(ContactLocation, id=loc_id)
            location.delete()
            return JsonResponse({"success": True, "message": "Location deleted successfully."})

        else:
            return JsonResponse({"success": False, "message": "Invalid action."})

    # GET request - just render page
    return render(request, 'backend/contactus_location.html', {"locations": locations})

def contactUs_msg(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest" and request.GET.get("msg_id"):
        msg_id = request.GET.get("msg_id")
        msg = get_object_or_404(ContactMessage, pk=msg_id)
        return JsonResponse({
            "name": msg.name,
            "email": msg.email,
            "number": msg.number,
            "website": msg.website or "-",
            "message": msg.message,
            "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M"),
        })

    messages = ContactMessage.objects.order_by("-created_at")
    return render(request, "backend/contactus_msg.html", {"messages": messages})



def product_list(request):
    return render(request, 'backend/product-list.html')

def add_product(request):
    return render(request, 'backend/product-add.html')

def category_list(request):
    return render(request, 'backend/category-list.html')

def order_list(request):
    return render(request, 'backend/order-list.html')

def order_detail(request):
    return render(request, 'backend/order-details.html')

def customer_list(request):
    return render(request, 'backend/customer-all.html')

def customer_overview(request):
    return render(request, 'backend/customer-details-overview.html')

def security(request):
    return render(request, 'backend/customer-details-security.html')

def billing(request):
    return render(request, 'backend/customer-details-billing.html')

def notification(request):
    return render(request, 'backend/customer-details-notifications.html')

def store_details(request):
    return render(request, 'backend/settings-detail.html')

def payments(request):
    return render(request, 'backend/settings-payments.html')

def checkout(request):
    return render(request, 'backend/settings-checkout.html')

def shipping(request):
    return render(request, 'backend/settings-shipping.html')

def location(request):
    return render(request, 'backend/settings-locations.html')

def setting_notification(request):
    return render(request, 'backend/settings-notifications.html')

def invoice_add(request):
    return render(request, 'backend/invoice-add.html')

def invoice_edit(request):
    return render(request, 'backend/invoice-edit.html')

def invoice_preview(request):
    return render(request, 'backend/invoice-preview.html')

def invoice_list(request):
    return render(request, 'backend/invoice-list.html')

def access_roles(request):
    return render(request, 'backend/access-roles.html')

def access_permission(request):
    return render(request, 'backend/access-permission.html')