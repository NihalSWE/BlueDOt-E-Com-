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

def home_banner(request):
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


def home_centerCard(request):
    if request.method == 'POST':
        CenterCard.objects.create(
            subtitle=request.POST.get('subtitle'),
            title=request.POST.get('title'),
            button_text=request.POST.get('button_text'),
            button_link=request.POST.get('button_link'),
            image=request.FILES.get('image')
        )
        return redirect('home_centerCard')  # adjust this if your URL name differs

    cards = CenterCard.objects.all()
    return render(request, 'backend/home_centerCard.html', {'cards': cards})
def edit_center_card(request, card_id):
    card = get_object_or_404(CenterCard, id=card_id)
    if request.method == 'POST':
        card.subtitle = request.POST.get('subtitle')
        card.title = request.POST.get('title')
        card.button_text = request.POST.get('button_text')
        card.button_link = request.POST.get('button_link')
        if 'image' in request.FILES:
            card.image = request.FILES['image']
        card.save()
        return redirect('home_centerCard')


def delete_center_card(request, card_id):
    card = get_object_or_404(CenterCard, id=card_id)
    if request.method == 'POST':
        card.delete()
    return redirect('home_centerCard')

# def home_CTA(request):
#     return render (request, 'backend/home_cta.html')



def practice_area(request):
    practice_areas = PracticeArea.objects.all().order_by('-created_at')
    
    context = {
        'practice_areas': practice_areas,
    }
    
    return render(request, 'backend/home_content/practice_area.html', context)


def practice_area_create(request):
    if request.method == 'POST':
        heading = request.POST.get('heading')
        description = request.POST.get('description')
        PracticeArea.objects.create(heading=heading, description=description)
        return redirect('practice_area')  # Change this to your actual success redirect
    return render(request, 'backend/home_content/practice_area_create.html')
    
    


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
    """Handle all FAQ operations in one view"""
    
    # Handle POST requests for different actions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            if action == 'create_update_section':
                # Create or update FAQ section
                faq_section = FAQSection.objects.first()
                
                if faq_section:
                    # Update existing section
                    faq_section.video_url = request.POST.get('video_url', faq_section.video_url)
                    faq_section.skill1_name = request.POST.get('skill1_name', faq_section.skill1_name)
                    faq_section.skill1_progress = int(request.POST.get('skill1_progress', faq_section.skill1_progress))
                    faq_section.skill2_name = request.POST.get('skill2_name', faq_section.skill2_name)
                    faq_section.skill2_progress = int(request.POST.get('skill2_progress', faq_section.skill2_progress))
                    faq_section.stat_icon_class = request.POST.get('stat_icon_class', faq_section.stat_icon_class)
                    faq_section.stat_title = request.POST.get('stat_title', faq_section.stat_title)
                    faq_section.stat_count = int(request.POST.get('stat_count', faq_section.stat_count))
                    faq_section.stat_description = request.POST.get('stat_description', faq_section.stat_description)
                    faq_section.section_subtitle = request.POST.get('section_subtitle', faq_section.section_subtitle)
                    faq_section.section_title = request.POST.get('section_title', faq_section.section_title)
                    
                    if 'video_thumbnail' in request.FILES:
                        faq_section.video_thumbnail = request.FILES['video_thumbnail']
                        
                    faq_section.save()
                    messages.success(request, 'FAQ Section updated successfully!')
                else:
                    # Create new section
                    faq_section = FAQSection.objects.create(
                        video_url=request.POST.get('video_url', ''),
                        video_thumbnail=request.FILES.get('video_thumbnail'),
                        skill1_name=request.POST.get('skill1_name', 'T-Shirt Printing'),
                        skill1_progress=int(request.POST.get('skill1_progress', 75)),
                        skill2_name=request.POST.get('skill2_name', 'Branding'),
                        skill2_progress=int(request.POST.get('skill2_progress', 85)),
                        stat_icon_class=request.POST.get('stat_icon_class', 'flaticon-roll'),
                        stat_title=request.POST.get('stat_title', 'Smooth Automation'),
                        stat_count=int(request.POST.get('stat_count', 428)),
                        stat_description=request.POST.get('stat_description', 'Printing Specialist'),
                        section_subtitle=request.POST.get('section_subtitle', 'FREQUENTLY ASKED QUESTION'),
                        section_title=request.POST.get('section_title', 'What Our Clients Ask About Presvila')
                    )
                    messages.success(request, 'FAQ Section created successfully!')
            
            elif action == 'create_faq_item':
                # Create new FAQ item
                faq_section = FAQSection.objects.first()
                if not faq_section:
                    messages.error(request, 'Please create FAQ section first!')
                else:
                    FAQItem.objects.create(
                        faq_section=faq_section,
                        question=request.POST.get('question', ''),
                        answer=request.POST.get('answer', ''),
                        is_expanded=request.POST.get('is_expanded') == 'on'
                    )
                    messages.success(request, 'FAQ item created successfully!')
            
            elif action == 'update_faq_item':
                # Update FAQ item
                item_id = request.POST.get('item_id')
                faq_item = get_object_or_404(FAQItem, id=item_id)
                faq_item.question = request.POST.get('question', faq_item.question)
                faq_item.answer = request.POST.get('answer', faq_item.answer)
                faq_item.is_expanded = request.POST.get('is_expanded') == 'on'
                faq_item.save()
                messages.success(request, 'FAQ item updated successfully!')
            
            elif action == 'delete_faq_item':
                # Delete FAQ item
                item_id = request.POST.get('item_id')
                faq_item = get_object_or_404(FAQItem, id=item_id)
                faq_item.delete()
                messages.success(request, 'FAQ item deleted successfully!')
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('aboutus_faq')
    
    # GET request - display the page
    faq_section = FAQSection.objects.first()
    faq_items = FAQItem.objects.all().order_by('id') if faq_section else []
    
    context = {
        'faq_section': faq_section,
        'faq_items': faq_items,
    }
    return render(request, 'backend/aboutUs_faq.html', context)





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


def Ourfaq_banner(request):
    banner = OurfaqBanner.objects.last()
    if not banner:
        banner = OurfaqBanner.objects.create()

    if request.method == 'POST':
        form = AboutUsBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faqs banner updated successfully!')
            return redirect('Ourfaq_banner')
    else:
        form = AboutUsBannerForm(instance=banner)

    return render(request, 'backend/OurFaq_banner.html', {
        'form': form,
        'banner': banner
    })
    
def Ourfaq_faqs(request):
    """Single view to handle all FAQ operations"""
    
    if request.method == 'POST':
        try:
            action = request.POST.get('action')

            if action == 'create':
                question = request.POST.get('question', '').strip()
                answer = request.POST.get('answer', '').strip()
                order = request.POST.get('order', 0)
                is_active = request.POST.get('is_active') == 'on'
                section_title = request.POST.get('section_title', '').strip()
                image = request.FILES.get('image')

                if question and answer:
                    faq = FAQ.objects.create(
                        question=question,
                        answer=answer,
                        order=int(order) if order else 0,
                        is_active=is_active,
                        section_title=section_title,
                        image=image
                    )
                    return JsonResponse({'success': True, 'message': 'FAQ created successfully!'})
                else:
                    return JsonResponse({'success': False, 'message': 'Question and Answer are required!'})

            elif action == 'update':
                faq_id = request.POST.get('faq_id')
                faq = get_object_or_404(FAQ, id=faq_id)

                faq.question = request.POST.get('question', '').strip()
                faq.answer = request.POST.get('answer', '').strip()
                faq.order = int(request.POST.get('order', 0) or 0)
                faq.is_active = request.POST.get('is_active') == 'on'
                faq.section_title = request.POST.get('section_title', '').strip()
                
                if 'image' in request.FILES:
                    faq.image = request.FILES['image']

                faq.save()

                return JsonResponse({'success': True, 'message': 'FAQ updated successfully!'})

            elif action == 'get':
                faq_id = request.POST.get('faq_id')
                faq = get_object_or_404(FAQ, id=faq_id)
                
                return JsonResponse({
                    'success': True,
                    'faq': {
                        'id': faq.id,
                        'question': faq.question,
                        'answer': faq.answer,
                        'order': faq.order,
                        'is_active': faq.is_active,
                        'section_title': faq.section_title,
                        'image_url': faq.image.url if faq.image else ''
                    }
                })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    faqs = FAQ.objects.all().order_by('order', '-created_at')
    context = {
        'faqs': faqs,
        'total_faqs': faqs.count(),
        'active_faqs': faqs.filter(is_active=True).count(),
    }

    return render(request, 'backend/OurFaq_faqs.html', context)
    
