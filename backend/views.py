from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms import modelformset_factory
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Brand
from django.views.decorators.csrf import csrf_exempt
from .models import Brand
import logging
import json
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth, TruncYear
from django.db import transaction
from django.db.models import Count, Avg
from django.utils.timezone import now
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_GET
# Create your views here.
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from decimal import Decimal
from django.db.models import Sum, Value, DecimalField, Q
from django.db.models.functions import Coalesce
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import IntegerField
from django.utils.timezone import localtime
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper, Value
from django.db.models.functions import Coalesce
from django.utils.dateparse import parse_date
from datetime import timedelta

from decimal import Decimal

@login_required
def dashboard(request):
    now = timezone.now()
    today = now.date()
    current_year = now.year
    
    # Calculate week range
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Weekly sales data with correct field names
    weekly_sales = MaterialInventoryDetail.objects.filter(
        mid_deal_type='sell',
        mid_entry_date__date__range=[start_of_week, end_of_week]
    ).select_related('mid_material', 'mid_material__mr_type')
    
    # Calculate weekly metrics
    weekly_metrics = weekly_sales.aggregate(
        total_qty=Sum('mid_sell_quentity'),
        total_earnings=Sum('mid_sell_prices'),
        total_cost=Sum('mid_buy_prices')
    )
    
    weekly_sell_qty = weekly_metrics['total_qty'] or 0
    weekly_earnings = weekly_metrics['total_earnings'] or 0
    weekly_profit = (weekly_earnings - (weekly_metrics['total_cost'] or 0))
    
    # Get top selling materials this week with correct field names
    top_materials = weekly_sales.values(
        'mid_material__mr_material_name',
        'mid_material__mr_type__TypeName'  # Changed from 'name' to 'TypeName'
    ).annotate(
        quantity=Sum('mid_sell_quentity'),
        earnings=Sum('mid_sell_prices')
    ).order_by('-earnings')[:8]
    
    # Group top materials by category for the slider
    material_categories = {}
    for material in top_materials:
        category_name = material.get('mid_material__mr_type__TypeName') or 'Other'  # Changed to TypeName
        if category_name not in material_categories:
            material_categories[category_name] = {
                'total_earnings': 0,
                'materials': []
            }
        material_categories[category_name]['total_earnings'] += material['earnings']
        material_categories[category_name]['materials'].append({
            'name': material['mid_material__mr_material_name'],
            'quantity': material['quantity']
        })
    
    # Prepare data for template
    weekly_sales_data = []
    for category, data in material_categories.items():
        weekly_sales_data.append({
            'name': category,
            'total_earnings': data['total_earnings'],
            'materials': data['materials'],
            'image': f"assets/img/products/card-weekly-sales-{category.lower().replace(' ', '-')}.png"
        })
    # Prepare data for template
    weekly_sales_data = []
    for category, data in material_categories.items():
        weekly_sales_data.append({
            'name': category,
            'total_earnings': data['total_earnings'],
            'materials': data['materials'],
            'image': f"assets/img/products/card-weekly-sales-{category.lower().replace(' ', '-')}.png"
        })
    
    # All inventory calculations
    inventory_details = MaterialInventoryDetail.objects.all()
    suppliers = {str(s.prs_slid): s for s in PartyRegSupplier.objects.all()}
    total_sell_qty = inventory_details.aggregate(
        total=Sum('mid_sell_quentity')
    )['total'] or 0
    
    total_profit = inventory_details.filter(
        mid_deal_type='sell'
    ).aggregate(
        profit=Sum('mid_sell_prices') - Sum('mid_buy_prices')
    )['profit'] or 0
    
    # Reviews data
    current_year_reviews = ProductReview.objects.filter(
        created_at__year=current_year
    )
    total_ratings = current_year_reviews.count()
    average_rating = current_year_reviews.aggregate(
        avg_rating=Avg('rating')
    )['avg_rating'] or 0
    average_rating = round(average_rating, 2)
    
    # Other metrics
    total_purchases = inventory_details.aggregate(
        total=Sum('mid_buy_paid')
    )['total'] or 0
    
    new_customers_count = CustomerInfo.objects.count() 
    total_transactions = inventory_details.filter(
        mid_deal_type='sell'
    ).count()

    visitor_counts = get_visitor_counts()
    mobile_visitors = visitor_counts['mobile']
    desktop_visitors = visitor_counts['desktop']
    total_visitors = mobile_visitors + desktop_visitors
    average_visitors = total_visitors / 2 
    # Format with commas as strings
    mobile_visitors_formatted = f"{mobile_visitors:,}"
    desktop_visitors_formatted = f"{desktop_visitors:,}"
    total_visitors_formatted = f"{total_visitors:,}"
    visitor_counts = get_visitor_counts()
    mobile_visitors = visitor_counts['mobile']
    desktop_visitors = visitor_counts['desktop']

    days = 7  # or your actual period count

    average_mobile = mobile_visitors / days
    average_desktop = desktop_visitors / days

    # Format with commas and no decimals
    mobile_visitors_formatted = f"{mobile_visitors:,}"
    desktop_visitors_formatted = f"{desktop_visitors:,}"
    average_mobile_formatted = f"{average_mobile:,.0f}"
    average_desktop_formatted = f"{average_desktop:,.0f}"
    sales_this_month = get_sales_this_month()

    # Format with commas and 2 decimals
    sales_this_month_formatted = f"{sales_this_month:,.2f}"
    total_orders = Order.objects.count()  # total orders count
    buy_data = (
        MaterialInventoryDetail.objects
        .values('mid_party')   # Just the CharField value
        .annotate(total_buy_quantity=Sum('mid_buy_quentity'))
        .order_by('mid_party')
    )
    
    supplier_names = [entry['mid_party'] for entry in buy_data]
    total_buy_quantities = [float(entry['total_buy_quantity']) for entry in buy_data]
    customer_names, total_buy_quantities = get_customer_buy_data()

    total_order_items = OrderItem.objects.count()  # total order items count
    users = User.objects.all().order_by('-id')[:10]  # last 10 users, adjust as needed
    last_10_orders = Order.objects.order_by('-created_at')[:10]
    context = {
        # Weekly sales data
        'weekly_sell_qty': weekly_sell_qty,
        'weekly_earnings': weekly_earnings,
        'weekly_profit': weekly_profit,
        'material_categories': weekly_sales_data,
        'start_of_week': start_of_week.strftime('%b %d'),
        'end_of_week': end_of_week.strftime('%b %d'),
         'users': users,
        # General metrics
        'total_sell_qty': total_sell_qty,
        'total_profit': total_profit,
        'new_customers_count': new_customers_count,
        'total_transactions': total_transactions,
        'total_ratings': total_ratings,
        'average_rating': average_rating,
        'current_year': current_year,
        'total_purchases': total_purchases,
        'sales_this_month': sales_this_month_formatted,

        'mobile_visitors': mobile_visitors_formatted,
        'desktop_visitors': desktop_visitors_formatted,
        'total_visitors': total_visitors_formatted,
           'average_mobile': average_mobile_formatted,
    'average_desktop': average_desktop_formatted,

            'total_orders': total_orders,
        'total_order_items': total_order_items,
                'supplier_names': supplier_names,
        'total_buy_quantities': total_buy_quantities,
                'customer_names': customer_names,
        'total_buy_quantities': total_buy_quantities,
           'last_10_orders': last_10_orders,
    
    }
    return render(request, 'backend/index.html', context)


def login_view(request):
    if request.method == 'POST':
        email_or_username = request.POST.get('email')
        password = request.POST.get('password')

        # Try authenticating with username
        user = authenticate(request, username=email_or_username, password=password)

        # If not found, try authenticating with email
        if user is None:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user_obj = User.objects.get(email=email_or_username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            return redirect('dashboard') 
        else:
            messages.error(request, 'Invalid email/username or password')

    return render(request, 'backend/user_authentication/login.html')


def custom_logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def user_list(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            email = request.POST.get('add_email')
            user_id = request.POST.get('add_user_id')
            name = request.POST.get('add_name')
            phone = request.POST.get('add_phone')
            user_type = request.POST.get('add_user_type')
            password = request.POST.get('add_password')

            # Validate fields
            if not all([email, user_id, name, phone, user_type, password]):
                messages.error(request, "All fields are required.")
                return redirect('user_list')

            # Check for duplicate email or user_id
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect('user_list')

            if User.objects.filter(user_id=user_id).exists():
                messages.error(request, "User ID already exists.")
                return redirect('user_list')

            try:
                user = User(
                    email=email,
                    user_id=user_id,
                    username=email,  # optional, you can change
                    phone_number=phone,
                    user_type=int(user_type),
                    name=name
                )
                user.set_password(password)
                user.save()
                messages.success(request, "User created successfully.")
            except Exception as e:
                messages.error(request, f"Error: {e}")

            return redirect('user_list')

    admin_users = User.objects.all()
    return render(request, 'backend/users/user_list.html', {
        'admin_users': admin_users,
    })
    
@login_required
def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        user_id_input = request.POST.get('user_id', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone_number', '').strip()
        user_type = request.POST.get('user_type')
        user_status = request.POST.get('user_status')
        password = request.POST.get('password', '').strip()  # Optional password update

        # Validate required fields
        if not name or not user_id_input or not email:
            messages.error(request, 'Name, User ID, and Email are required.')
            return redirect('user_list')

        # Check for duplicate email or user_id (excluding current user)
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'Email already exists.')
            return redirect('user_list')

        if User.objects.filter(user_id=user_id_input).exclude(id=user.id).exists():
            messages.error(request, 'User ID already exists.')
            return redirect('user_list')

        # Save updated values
        user.name = name
        user.user_id = user_id_input
        user.email = email
        user.phone_number = phone
        user.user_type = user_type
        user.user_status = user_status

        if password:
            user.set_password(password)  # Secure password update

        user.save()
        messages.success(request, 'User updated successfully.')

    return redirect('user_list')
    
@login_required
def delete_user(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
    
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('user_list')

@login_required
@require_GET
def last_10_orders_api(request):
    # Get last 10 orders, newest first
    last_10_orders = Order.objects.order_by('-created_at')[:10]

    # Prepare data for chart: count orders by status
    # We'll map statuses to names and count how many orders per status in these 10
    status_map = dict(Order.STATUS_CHOICES)  # e.g. {0: 'Pending', 1: 'Approved', ...}

    # Count how many orders per status in last 10 orders
    status_counts = {key: 0 for key in status_map.keys()}
    for order in last_10_orders:
        # order.status might be string because CharField but your choices keys are int? 
        # Convert to int if needed:
        try:
            status_key = int(order.status)
        except:
            status_key = order.status
        if status_key in status_counts:
            status_counts[status_key] += 1

    # Format response data
    response_data = {
        'labels': [status_map[key] for key in status_counts.keys()],
        'data': [status_counts[key] for key in status_counts.keys()],
    }

    return JsonResponse(response_data)
@login_required
def get_last_user():
    return User.objects.order_by('-created_at').first()  # Or order_by('-id')

def get_customer_buy_data():
    buy_data = (
        MaterialInventoryDetail.objects
        .filter(mid_deal_type='buy', mid_order_id__isnull=False)
        .annotate(
            customer_name=F('mid_order_id__customer__CustomerName')
        )
        .values('customer_name')
        .annotate(total_buy_quantity=Sum('mid_buy_quentity'))
        .order_by('customer_name')
    )

    customer_names = [entry['customer_name'] or "Unknown" for entry in buy_data]
    total_buy_quantities = [float(entry['total_buy_quantity'] or 0) for entry in buy_data]

    return customer_names, total_buy_quantities

def get_sales_this_month():
    today = now()
    current_month = today.month
    current_year = today.year

    sales_total = MaterialInventoryDetail.objects.filter(
        mid_deal_type='sell',
        mid_entry_date__year=current_year,
        mid_entry_date__month=current_month
    ).aggregate(total_sales=Sum('mid_sell_prices'))['total_sales'] or 0

    return sales_total

def get_visitor_counts():
    mobile_visitors = Visitor.objects.filter(device_type='mobile').count()
    desktop_visitors = Visitor.objects.filter(device_type='desktop').count()
    return {
        'mobile': mobile_visitors,
        'desktop': desktop_visitors
    }

def get_weekly_sales_data():
    from datetime import timedelta, date
    today = date.today()
    last_week = today - timedelta(days=7)

    sales = (
        MaterialInventoryDetail.objects
        .filter(mid_deal_type='sell', mid_entry_date__date__gte=last_week)
        .values('mid_material__mr_type__name')  # Group by material type name
        .annotate(total_quantity=Sum('mid_sell_quentity'))
    )
    return sales
@login_required
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

@login_required
def home_CTA(request):
    cta = HomeCTA.objects.first()
    if request.method == "POST":
        form = HomeCallToActionForm(request.POST, request.FILES, instance=cta)
        if form.is_valid():
            form.save()
            return redirect('home_CTA')
    else:
        form = HomeCallToActionForm(instance=cta)
    return render(request, 'backend/home_cta.html', {
        'form': form,
        'cta': cta,
    })


@login_required
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
@login_required
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

@login_required
def delete_center_card(request, card_id):
    card = get_object_or_404(CenterCard, id=card_id)
    if request.method == 'POST':
        card.delete()
    return redirect('home_centerCard')

# def home_CTA(request):
#     return render (request, 'backend/home_cta.html')

@login_required
def practice_area(request):
    practice_areas = PracticeArea.objects.all().order_by('-created_at')
    
    context = {
        'practice_areas': practice_areas,
    }
    
    return render(request, 'backend/home_content/practice_area.html', context)

@login_required
def practice_area_create(request):
    if request.method == 'POST':
        heading = request.POST.get('heading')
        description = request.POST.get('description')
        PracticeArea.objects.create(heading=heading, description=description)
        return redirect('practice_area')  # Change this to your actual success redirect
    return render(request, 'backend/home_content/practice_area_create.html')
    
    

@login_required
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


@login_required
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
@login_required
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

@login_required
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




@login_required
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
@login_required
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
@login_required
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


@login_required
def order_list(request):
    return render(request, 'backend/orders/order_list.html')

# def create_order(request):
#     customers = CustomerInfo.objects.all()
#     products = Product.objects.all()
#     materials = MaterialRegistration.objects.all()
#     units = Unit.objects.all()
    
#     if request.method == 'POST':
#         try:
#             customer_id = int(request.POST.get('customer'))
#             order_date = request.POST.get('order_date')
#             notes = request.POST.get('notes', '')
#             product_id = int(request.POST.get('product_id', ''))
#             materials_ids = request.POST.getlist('materials[]')
#             units_ids = request.POST.getlist('units[]')
#             quantities = request.POST.getlist('quantities[]')
            
#             if customer_id and product_id:
#                 customer = Customer.objects.filter(id=customer_id).first()
#                 product = Product.objects.filter(id=product_id).first()
                
#                 return messages.error(request, f'Error creating order: {str(e)}')
            
#             if customer and product:
#                 # Create the order
#                 order = Order.objects.create(
#                     customer_id=customer_id,
#                     order_date=order_date,
#                     notes=notes,
#                     status='pending'
#                 )
                
#                 # Add order items
#                 for material_id, unit_id, quantity in zip(materials_ids, units_ids, quantities):
#                     OrderItem.objects.create(
#                         order=order,
#                         material_id=material_id,
#                         unit_id=unit_id,
#                         quantity=quantity
#                     )
            
#             return redirect('order_list')
            
#         except Exception as e:
#             messages.error(request, f'Error creating order: {str(e)}')
    
#     context = {
#         'customers': customers,
#         'products': products,
#         'materials': materials,
#         'units': units,
#     }
    
#     return render(request, 'backend/orders/create.html', context)

def initial_orders(request):
    customers = CustomerInfo.objects.all()
    products = Product.objects.all()
    
    orders = Order.objects.all().select_related('customer').prefetch_related('items__product')
    
    user_type = None  # <-- define it early to avoid UnboundLocalError

    if request.user.is_authenticated:
        print('The user is authenticated')
        user = request.user
        user_type = user.user_type
        
    print('user in initial orders: ', user)
    
    context = {
        'customers': customers,
        'products': products,
        'orders': orders,
        'user_type': user_type,
    }
    return render(request, 'backend/orders/initial_orders.html', context)


def initial_order_create(request):
    customers = CustomerInfo.objects.all()
    products = Product.objects.all()
    
    if request.method == 'POST':
        try:
            # Get form data
            customer_id = request.POST.get('customer')
            order_notes = request.POST.get('notes', '')
            
            # Validate customer
            if not customer_id:
                messages.error(request, 'Please select a customer')
                return redirect('initial_order_create')
            
            # Create the order
            order = Order.objects.create(
                customer_id=customer_id,
                order_date=timezone.now(),
                status=0,
                notes=order_notes
            )
            
            # Get product data from the form
            product_ids = request.POST.getlist('products[]')
            quantities = request.POST.getlist('quantities[]')
            product_notes = request.POST.getlist('notes[]')
            
            # Validate products
            if not product_ids:
                order.delete()  # Rollback if no products
                messages.error(request, 'Please add at least one product to the order')
                return redirect('initial_order_create')
            
            # Create order items with notes
            for product_id, quantity, note in zip(product_ids, quantities, product_notes):
                try:
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        notes=note  # Add product-specific notes
                    )
                except Product.DoesNotExist:
                    continue
            
            messages.success(request, 'Order created successfully!')
            return redirect('initial_orders')
            
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
            return redirect('initial_order_create')
    
    context = {
        'customers': customers,
        'products': products,
    }
    return render(request, 'backend/orders/initial_order_create.html', context)


def initial_order_update(request, id):
    order = get_object_or_404(Order, id=id)
    customers = CustomerInfo.objects.all()
    products = Product.objects.all()

    if request.method == 'POST':
        product_ids = request.POST.getlist('products[]')
        quantities = request.POST.getlist('quantities[]')
        notes = request.POST.getlist('notes[]')

        if not product_ids:
            messages.error(request, 'Please select at least one product.')
        else:
            try:
                # Clear existing items for this order
                OrderItem.objects.filter(order=order).delete()

                # Add updated items
                for i in range(len(product_ids)):
                    product = get_object_or_404(Product, id=product_ids[i])
                    quantity = int(quantities[i])
                    note = notes[i]

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        notes=note
                    )

                messages.success(request, 'Order updated successfully.')
                return redirect('initial_order_update', id=order.id)
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

    # Prepare selected items for pre-population in table
    order_items = OrderItem.objects.filter(order=order).select_related('product')
    selected_items = []
    for item in order_items:
        selected_items.append({
            'product': item.product,
            'quantity': item.quantity,
            'notes': item.notes,
            'total': item.quantity * item.product.base_price
        })

    return render(request, 'backend/orders/initial_order_update.html', {
        'order': order,
        'products': products,
        'customers': customers,
        'order_items': selected_items,
    })

# def approve_order(request, id):
#     order = Order.objects.filter(id=id).first()
#     customers = CustomerInfo.objects.all()
#     products = Product.objects.all()
#     materials = MaterialRegistration.objects.all()
#     units = Unit.objects.all()
    
#     if not order:
#         messages.error(request, 'Order not found.')
#         raise ValueError("Missing Order.")
    
#     order_items = order.items.all()
#     print('order_items: ', order_items)
        

#     if request.method == 'POST':
#         try:
#             customer_id = request.POST.get('customer')
#             product_id = request.POST.get('product_id')
#             order_date = request.POST.get('order_date')
#             notes = request.POST.get('notes', '')
#             materials_ids = request.POST.getlist('materials[]')
#             units_ids = request.POST.getlist('units[]')
#             quantities = request.POST.getlist('quantities[]')

#             # Basic Validation
#             if not customer_id:
#                 messages.error(request, "Customer is required.")
#                 raise ValueError("Missing customer.")

#             if not product_id:
#                 messages.error(request, "Product is required.")
#                 raise ValueError("Missing product.")

#             if not materials_ids:
#                 messages.error(request, "At least one material is required.")
#                 raise ValueError("Missing materials.")

#             if len(materials_ids) != len(units_ids) or len(materials_ids) != len(quantities):
#                 messages.error(request, "Each material must have corresponding unit and quantity.")
#                 raise ValueError("Material/Unit/Quantity mismatch.")

#             customer = CustomerInfo.objects.filter(id=customer_id).first()
#             product = Product.objects.filter(id=product_id).first()

#             if not customer or not product:
#                 messages.error(request, "Invalid customer or product.")
#                 raise ValueError("Invalid customer/product.")

#             # Create Order
#             order = Order.objects.create(
#                 customer=customer,
#                 status='pending',
#                 notes=notes,
#             )

#             # Add Order Item
#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=1
#             )

#             # Add Material Usage
#             for material_id, unit_id, qty in zip(materials_ids, units_ids, quantities):
#                 if not qty or float(qty) <= 0:
#                     messages.warning(request, f"Skipped material ID {material_id} due to invalid quantity.")
#                     continue

#                 material = MaterialRegistration.objects.filter(id=material_id).first()
#                 unit = Unit.objects.filter(id=unit_id).first()

#                 if not material or not unit:
#                     messages.warning(request, f"Invalid material or unit for ID {material_id}, {unit_id}. Skipped.")
#                     continue

#                 MaterialUsage.objects.create(
#                     order=order,
#                     material=material,
#                     unit=unit,
#                     quantity_used=qty
#                 )

#                 # Log inventory usage
#                 InventoryLog.objects.create(
#                     material=material,
#                     change_type='out',
#                     quantity_changed=qty,
#                     reference=f"Order #{order.id}"
#                 )

#             messages.success(request, "Order created successfully.")
#             return redirect('order_list')

#         except Exception as e:
#             messages.error(request, f"Error creating order: {str(e)}")

#     context = {
#         'customers': customers,
#         'products': products,
#         'materials': materials,
#         'units': units,
#         'order_items': order_items,
#     }
#     return render(request, 'backend/orders/approve_order.html', context)


# Approve Order Starts
def approve_order(request, id):
    order = get_object_or_404(Order, id=id)
    customers = CustomerInfo.objects.all()
    materials = MaterialRegistration.objects.all()
    units = Unit.objects.all()
    order_items = order.items.all()

    if request.method == 'POST':
        try:
            with transaction.atomic():
                _update_order_fields(order, request)
                print( 'order status before entering: ', order.status)

                for item in order_items:
                    _process_material_usages(order, item, request)
                    print( 'order status after saving materials: ', order.status)

                if int(order.status) == 2:
                    print('got order_status------------------------: ', order.status)
                    _update_inventory_details(order, request.user)

                messages.success(request, "Order approved and materials saved.")
                return redirect('initial_orders')

        except Exception as exc:
            messages.error(request, f"Error: {exc}")
            raise

    user_type = request.user.user_type if request.user.is_authenticated else None

    for item in order_items:
        for usage in item.material_usages.all():
            usage.total_price = usage.quantity_used * usage.material.mr_sell_price

    added_materials_dict = {}
    for item in order_items:
        for usage in item.material_usages.all():
            added_materials_dict[usage.material.id] = {
                'product_id': item.product.id,
                'product_name': item.product.name,
                'unit_id': usage.unit.id,
                'quantity': usage.quantity_used,
            }

    product_material_map = defaultdict(list)
    for item in order_items:
        for usage in item.material_usages.all():
            product_material_map[item.product.id].append(usage.material.id)

    return render(request, 'backend/orders/approve_order.html', {
        'order': order,
        'customers': customers,
        'materials': materials,
        'units': units,
        'order_items': order_items,
        'added_materials_dict': added_materials_dict,
        'user_type': user_type,
        'product_material_map': dict(product_material_map),
    })

def _update_order_fields(order, request):
    customer_id = request.POST.get('customer')
    order_date = request.POST.get('order_date')
    notes = request.POST.get('notes', '')
    order_status = int(request.POST.get('order_status') or 1)
    
    print('order_status: ', order_status)

    customer = CustomerInfo.objects.filter(id=customer_id).first()
    if not customer:
        raise ValueError("Customer invalid.")

    order.customer = customer
    order.order_date = order_date
    order.notes = notes
    order.status = order_status
    order.save()

# def _process_material_usages(order, item, request):
#     prod_id = item.product.id

#     mat_ids = request.POST.getlist(f'materials_{prod_id}[]')
#     unit_ids = request.POST.getlist(f'units_{prod_id}[]')
#     qtys = request.POST.getlist(f'quantities_{prod_id}[]')
    
#     print('//////////////mat_ids/////////////////', mat_ids)
#     print('//////////////unit_ids/////////////////', unit_ids)
#     print('//////////////qtys/////////////////', qtys)   

#     if not mat_ids or len(mat_ids) != len(unit_ids) or len(mat_ids) != len(qtys):
#         return

#     for mat_id, unit_id, qty_str in zip(mat_ids, unit_ids, qtys):
#         try:
#             qty = Decimal(qty_str)
#             if qty <= 0:
#                 continue
#         except (InvalidOperation, ValueError):
#             continue

#         material = MaterialRegistration.objects.filter(id=mat_id).first()
#         unit = Unit.objects.filter(id=unit_id).first()
#         if not material or not unit:
#             continue

#         usage, created = MaterialUsage.objects.get_or_create(
#             order_item=item,
#             material=material,
#             defaults={
#                 'order': order,
#                 'unit': unit,
#                 'quantity_used': qty
#             }
#         )

#         if not created:
#             usage.unit = unit
#             usage.quantity_used = qty
#             usage.save()

#         material.mr_quantity -= qty
#         material.save()


def _process_material_usages(order, item, request): 
    prod_id = item.product.id

    mat_ids = request.POST.getlist(f'materials_{prod_id}[]')
    unit_ids = request.POST.getlist(f'units_{prod_id}[]')
    qtys = request.POST.getlist(f'quantities_{prod_id}[]')
    
    print('//////////////mat_ids/////////////////', mat_ids)
    print('//////////////unit_ids/////////////////', unit_ids)
    print('//////////////qtys/////////////////', qtys)

    if not mat_ids or len(mat_ids) != len(unit_ids) or len(mat_ids) != len(qtys):
        return

    mat_ids_int = [int(mid) for mid in mat_ids]
    existing_usages = item.material_usages.all()

    # Delete usages that were removed in the form
    for usage in existing_usages:
        if usage.material.id not in mat_ids_int:
            # Restore stock before deleting
            usage.material.mr_quantity -= usage.quantity_used
            usage.material.save()
            usage.delete()

    total_material_cost = Decimal('0.00')

    for mat_id, unit_id, qty_str in zip(mat_ids, unit_ids, qtys):
        print('******mat_id***** ', mat_id)
        print('******unit_id***** ', unit_id)
        print('******qty_str***** ', qty_str)
        print('----------------------------------------------------------------------------------------------------')
        try:
            qty = Decimal(qty_str) * Decimal(item.quantity)
            if qty <= 0:
                continue
        except (InvalidOperation, ValueError):
            continue

        material = MaterialRegistration.objects.filter(id=mat_id).first()
        unit = Unit.objects.filter(id=unit_id).first()
        if not material or not unit:
            print('----material not found----')
            continue

        print('--------material get or create')
        usage, created = MaterialUsage.objects.get_or_create(
            order_item=item,
            material=material,
            defaults={
                'order': order,
                'unit': unit,
                'quantity_used': qty
            }
        )

        if not created:
            print('-----material not ceated------')
            # Restore stock difference
            material.mr_quantity += usage.quantity_used  # revert old usage
            usage.unit = unit
            usage.quantity_used = qty
            usage.save()

        # Reduce updated stock
        material.mr_quantity -= qty
        material.save()

        total_material_cost += material.mr_sell_price * qty

    # Update item pricing
    if total_material_cost > 0:
        try:
            quantity = Decimal(item.quantity)
            item.unit_price = total_material_cost
            item.total_price = total_material_cost * quantity
            item.save()
        except (InvalidOperation, ZeroDivisionError):
            pass
        
    

def _update_inventory_details(order, user):
    for item in order.items.all():
        for usage in item.material_usages.all():
            material = usage.material
            print('material usages **********: ', material)
            inv = MaterialInventoryDetail.objects.filter(mid_material=material).first()
            
            print('material inventory ----------: ', inv)

            if inv:
                inv.mid_order_id = order
                inv.mid_party = order.customer.id
                inv.mid_sell_quentity = usage.quantity_used
                inv.mid_sell_prices = material.mr_sell_price
                inv.mid_sell_paid = material.mr_sell_price * usage.quantity_used
                inv.mid_deal_type = 'sell'
                inv.mid_debit = material.mr_sell_price * usage.quantity_used
                inv.mid_entry_by = user
                inv.save()
                
                
def get_materials_by_product(request, order_id, product_id):
    usages = MaterialUsage.objects.filter(
        order_id=order_id,
        order_item__product_id=product_id
    ).select_related('material', 'unit')

    data = [
        {
            'material_id': usage.material.id,
            'material_name': usage.material.mr_material_name,
            'quantity': str(usage.quantity_used / usage.order_item.quantity),
            'unit_id': usage.unit.id,
        }
        for usage in usages
    ]
    return JsonResponse({'materials': data})
    

def order_detail(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('initial_orders')  # or a 404 page

    order_items = order.items.all().prefetch_related('material_usages__material')
    
    order_total_price = Decimal('0.00')  # Initialize total price
    for item in order_items:
        order_total_price += item.total_price

    return render(request, 'backend/orders/order-detail.html', {
        'order': order,
        'order_items': order_items,
        'order_total_price': order_total_price
    })

# Approve Order Ends


@login_required
def product_list(request):
    return render(request, 'backend/product-list.html')
@login_required
def add_product(request):
    return render(request, 'backend/product-add.html')

@login_required
def customer_list(request):
    return render(request, 'backend/customer-all.html')
@login_required
def customer_overview(request):
    return render(request, 'backend/customer-details-overview.html')
@login_required
def security(request):
    return render(request, 'backend/customer-details-security.html')
@login_required
def billing(request):
    return render(request, 'backend/customer-details-billing.html')
@login_required
def notification(request):
    return render(request, 'backend/customer-details-notifications.html')
@login_required
def store_details(request):
    return render(request, 'backend/settings-detail.html')
@login_required
def payments(request):
    return render(request, 'backend/settings-payments.html')
@login_required
def checkout(request):
    return render(request, 'backend/settings-checkout.html')
@login_required
def shipping(request):
    return render(request, 'backend/settings-shipping.html')
@login_required
def location(request):
    return render(request, 'backend/settings-locations.html')

def setting_notification(request):
    return render(request, 'backend/settings-notifications.html')
@login_required
def invoice_add(request):
    return render(request, 'backend/invoice-add.html')
@login_required
def invoice_edit(request):
    return render(request, 'backend/invoice-edit.html')
@login_required
def invoice_preview(request):
    return render(request, 'backend/invoice-preview.html')
@login_required
def invoice_list(request):
    return render(request, 'backend/invoice-list.html')
@login_required
def access_roles(request):
    return render(request, 'backend/access-roles.html')
@login_required
def access_permission(request):
    return render(request, 'backend/access-permission.html')

@login_required
def category_list(request):
    categories = Category.objects.all().order_by('-created_at')
    
    context = {
        'categories': categories,
    }

    return render(request, 'backend/categories/category_list.html', context)

@login_required
def category_create(request):
    parent_categories = Category.objects.filter(parent_category__isnull=True)

    if request.method == 'POST':
        name = request.POST.get('name')
        parent_id = request.POST.get('parent_category') or None
        description = request.POST.get('description')
        image = request.FILES.get('image')
        banner_image = request.FILES.get('banner_image')

        try:
            category = Category(
                name=name,
                description=description,
                image=image,
                banner_image=banner_image
            )

            if parent_id:
                category.parent_category = Category.objects.get(id=parent_id)

            category.save()
            messages.success(request, 'Category created successfully.')
            return redirect('category_list')  # update with actual name
        except Exception as e:
            messages.error(request, f'Failed to create category: {str(e)}')

    return render(request, 'backend/categories/create.html', {
        'parent_categories': parent_categories
    })
    
    
# @csrf_exempt  # Optional if you're using fetch and passing the CSRF token manually
@login_required
def update_category(request, pk):
    if request.method == "POST":
        category = get_object_or_404(Category, id=pk)

        # Update basic fields
        category.name = request.POST.get('edit_name', category.name)
        category.description = request.POST.get('edit_description', category.description)

        parent_id = request.POST.get('edit_parent_category')
        if parent_id:
            if str(category.id) != parent_id:  # Prevent self as parent
                category.parent_category_id = parent_id
        else:
            category.parent_category = None

        # Handle image update
        if 'edit_image' in request.FILES:
            category.image = request.FILES['edit_image']

        if 'edit_banner_image' in request.FILES:
            category.banner_image = request.FILES['edit_banner_image']

        category.save()

        return JsonResponse({'message': 'Category updated successfully.'})
    
    
@login_required
def delete_category(request, pk):
    if request.method == "POST":
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return redirect('category_list')
    
@login_required   
@require_http_methods(["GET", "POST"])
def units(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            name = request.POST.get('name')
            symbol = request.POST.get('symbol')
            Unit.objects.create(name=name, symbol=symbol)
            return redirect('units')  # change to your URL name

        elif action == 'edit':
            unit_id = request.POST.get('id')
            unit = get_object_or_404(Unit, pk=unit_id)
            unit.name = request.POST.get('name')
            unit.symbol = request.POST.get('symbol')
            unit.save()
            return redirect('units')

        elif action == 'delete':
            unit_id = request.POST.get('id')
            unit = get_object_or_404(Unit, pk=unit_id)
            unit.delete()
            return redirect('units')

    units = Unit.objects.all()
    return render(request, 'backend/units/unit_list.html', {'units': units})
    
@login_required 
# List brands (returns HTML)
@require_http_methods(["GET"])
def brand_list(request):
    brands = Brand.objects.filter(status=1)  # Only active brands
    return render(request, 'backend/brand/index.html', {'brands': brands})

# Create brand (returns JSON)

@login_required
@csrf_exempt
def brand_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        status = request.POST.get('status')
        image = request.FILES.get('image')

        if not name:
            return JsonResponse({'error': 'Brand name is required'}, status=400)

        brand = Brand(name=name, status=status)
        if image:
            brand.image = image
        brand.save()

        return JsonResponse({'success': True, 'brand_id': brand.id})

    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
# Get single brand (returns JSON)
@require_http_methods(["GET"])
def brand_detail(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    return JsonResponse({
        'id': brand.id,
        'name': brand.name,
        'image': brand.image.url if brand.image else None,  # assuming ImageField
        'status': brand.status,
        'created_at': brand.created_at.isoformat() if brand.created_at else None,
        'updated_at': brand.updated_at.isoformat() if brand.updated_at else None
    })

@login_required
# Update brand (returns JSON)
@csrf_exempt
@require_http_methods(["PUT", "POST"])
def brand_update(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    try:
        # For PUT and POST, parse JSON body
        data = json.loads(request.body.decode('utf-8'))
        
        brand.name = data.get('name', brand.name)
        
        # Handle image update carefully - this depends on how image upload is sent.
        # If image is a URL or base64 string, you'll need special handling.
        # Here we just skip updating image as json won't have file.
        
        brand.status = data.get('status', brand.status)
        brand.save()
        return JsonResponse({
            'id': brand.id,
            'name': brand.name,
            'image': brand.image.url if brand.image else None,
            'status': brand.status,
            'message': 'Brand updated successfully'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
# Delete brand (returns JSON)
@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    try:
        brand.delete()
        return JsonResponse({'message': 'Brand deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    
    context = {
        'products': products,
    }
    return render(request, 'backend/products/product_list.html', context)
@login_required
def product_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        base_price = request.POST.get('base_price')
        description = request.POST.get('description')
        thumbnail = request.FILES.get('thumbnail')

        category = Category.objects.get(id=category_id) if category_id else None
        brand = Brand.objects.get(id=brand_id) if brand_id else None

        product = Product.objects.create(
            name=name,
            category=category,
            brand=brand,
            base_price=base_price,
            description=description,
            thumbnail=thumbnail,
        )

        # Handle additional images
        for file in request.FILES.getlist('images'):
            if file:
                ProductImage.objects.create(product=product, image=file)

        return redirect('product_list')  # or wherever you want to redirect

    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'backend/products/create.html', {'categories': categories, 'brands': brands})
    
@login_required
def delete_product(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        messages.success(request, "Product deleted successfully.")
    return redirect('product_list')  # or wherever your list view is

@login_required
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

@login_required
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


@login_required   
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

@login_required
def home_CTA(request):
    cta = HomeCTA.objects.first()

    if request.method == "POST":
        form = HomeCallToActionForm(request.POST, request.FILES, instance=cta)
        if form.is_valid():
            form.save()
            return redirect('home_CTA')
    else:
        form = HomeCallToActionForm(instance=cta)

    return render(request, 'backend/home_cta.html', {
        'form': form,
        'cta': cta,
    })
    
    
@login_required   
def pricing_card(request):
    card, _ = PricingCard.objects.get_or_create(id=1)  # Ensure single editable instance

    if request.method == 'POST':
        form = PricingCardForm(request.POST, request.FILES, instance=card)
        if form.is_valid():
            form.save()
            return redirect('pricing_card')  # your URL name
    else:
        form = PricingCardForm(instance=card)

    return render(request, 'backend/home_pricingcard.html', {'form': form})


@login_required
def party_supplier_list(request):
    # List all suppliers (returns HTML)
    suppliers = PartyRegSupplier.objects.all()
    context = {'suppliers': suppliers}
    return render(request, 'backend/party_supplier/list.html', context)
@login_required
def party_supplier_detail(request, slid):
    # View details of a specific supplier (returns JSON)
    supplier = get_object_or_404(PartyRegSupplier, prs_slid=slid)
    data = {
        'prs_slid': supplier.prs_slid,
        'prs_name': supplier.prs_name,
        'prs_address': supplier.prs_address,
        'prs_person': supplier.prs_person,
        'prs_mobile': supplier.prs_mobile,
        'prs_phone': supplier.prs_phone,
        'prs_email': supplier.prs_email,
        'prs_website': supplier.prs_website,
        'prs_complain_number': supplier.prs_complain_number,
        'prs_reg_date': supplier.prs_reg_date,
        'loginidno': supplier.loginidno,
        'open_sdue': supplier.open_sdue
    }
    return JsonResponse(data)


logger = logging.getLogger(__name__)

@csrf_exempt  # Only use this if CSRF tokens are not being used (e.g., API endpoint)

@login_required
def party_supplier_create(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)

        # Validate required fields
        required_fields = ['prs_name', 'prs_reg_date']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'status': 'error', 'message': f'{field} is required'}, status=400)

        # Auto-generate prs_slid (e.g., SUP001, SUP002, ...)
        last_supplier = PartyRegSupplier.objects.order_by('-prs_slid').first()

        if last_supplier and last_supplier.prs_slid.startswith('SUP'):
            try:
                last_num = int(last_supplier.prs_slid.replace('SUP', ''))
                new_slid = f"SUP{last_num + 1:03d}"
            except ValueError:
                new_slid = "SUP001"
        else:
            new_slid = "SUP001"

        # Create new supplier record
        supplier = PartyRegSupplier.objects.create(
            prs_slid=new_slid,
            prs_name=data.get('prs_name', '').strip(),
            prs_address=data.get('prs_address', '').strip(),
            prs_person=data.get('prs_person', '').strip(),
            prs_mobile=data.get('prs_mobile', '').strip(),
            prs_phone=data.get('prs_phone', '').strip(),
            prs_email=data.get('prs_email', '').strip(),
            prs_website=data.get('prs_website', '').strip(),
            prs_complain_number=data.get('prs_complain_number', '').strip(),
            prs_reg_date=data.get('prs_reg_date'),
            loginidno=data.get('loginidno'),
            open_sdue=data.get('open_sdue') or 0,
        )

        return JsonResponse({'status': 'success', 'prs_slid': supplier.prs_slid}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
    except Exception as e:
        logger.exception("Error creating PartyRegSupplier")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    


@csrf_exempt
@login_required
def party_supplier_update(request, slid):
    if request.method == 'GET':
        try:
            supplier = PartyRegSupplier.objects.get(prs_slid=slid)
            data = {
                'prs_slid': supplier.prs_slid,
                'prs_name': supplier.prs_name,
                'prs_address': supplier.prs_address,
                'prs_person': supplier.prs_person,
                'prs_mobile': supplier.prs_mobile,
                'prs_phone': supplier.prs_phone,
                'prs_email': supplier.prs_email,
                'prs_website': supplier.prs_website,
                'prs_complain_number': supplier.prs_complain_number,
                 'prs_reg_date': supplier.prs_reg_date if supplier.prs_reg_date else '',
                'open_sdue': supplier.open_sdue,
            }
            return JsonResponse(data)
        except PartyRegSupplier.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Supplier not found'}, status=404)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            supplier = PartyRegSupplier.objects.get(prs_slid=slid)

            supplier.prs_name = data.get('prs_name')
            supplier.prs_address = data.get('prs_address')
            supplier.prs_person = data.get('prs_person')
            supplier.prs_mobile = data.get('prs_mobile')
            supplier.prs_phone = data.get('prs_phone')
            supplier.prs_email = data.get('prs_email')
            supplier.prs_website = data.get('prs_website')
            supplier.prs_complain_number = data.get('prs_complain_number')
            supplier.prs_reg_date = data.get('prs_reg_date')
            supplier.open_sdue = data.get('open_sdue') or 0

            supplier.save()
            return JsonResponse({'status': 'success'})
        except PartyRegSupplier.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Supplier not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
        
@login_required
def party_supplier_delete(request, slid):
    # Delete a supplier (returns JSON)
    supplier = get_object_or_404(PartyRegSupplier, prs_slid=slid)
    try:
        supplier.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    



@login_required
# List all material types
def material_type_list(request):
    material_types = MaterialType.objects.all()
    return render(request, 'backend/material/type/type_list.html', {'material_types': material_types})
@login_required
# Show form and create new material type
def material_type_create(request):
    if request.method == 'POST':
        type_name = request.POST.get('TypeName')
        adminid = request.user.id if request.user.is_authenticated else None

        if type_name:
            MaterialType.objects.create(TypeName=type_name, adminid=adminid)
            return redirect('material_type_list')
        else:
            return HttpResponse("TypeName is required", status=400)
    return render(request, 'material_type_form.html')
@login_required
# Show form and update existing material type
def material_type_update(request, id):
    material_type = get_object_or_404(MaterialType, pk=id)
    if request.method == 'POST':
        type_name = request.POST.get('TypeName')
        adminid = request.user.id if request.user.is_authenticated else None

        if type_name:
            material_type.TypeName = type_name
            material_type.adminid = adminid
            material_type.save()
            return redirect('material_type_list')
        else:
            return HttpResponse("TypeName is required", status=400)
    return render(request, 'material_type_form.html', {'material_type': material_type})
@login_required
# Delete a material type
@require_http_methods(["POST"])
def material_type_delete(request, pk):
    material_type = get_object_or_404(MaterialType, pk=pk)
    material_type.delete()
    return redirect('material_type_list')





@login_required
def material_list(request):
    materials = MaterialRegistration.objects.select_related('mr_supplier', 'mr_type', 'unit')

    suppliers = PartyRegSupplier.objects.all()
    types = MaterialType.objects.all()
    units = Unit.objects.all()

    zero_decimal = Value(0, output_field=DecimalField(max_digits=10, decimal_places=2))

    materials = materials.annotate(
        total_buy=Coalesce(Sum('inventory_entries__mid_buy_quentity'), zero_decimal),
        total_sell=Coalesce(Sum('inventory_entries__mid_sell_quentity'), zero_decimal),
        stock=ExpressionWrapper(
            Coalesce(Sum('inventory_entries__mid_buy_quentity'), zero_decimal) -
            Coalesce(Sum('inventory_entries__mid_sell_quentity'), zero_decimal),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )

    return render(request, 'backend/material/material_list.html', {
        'materials': materials,
        'suppliers': suppliers,
        'types': types,
        'units': units,
    })
# Create a new material
@login_required
def material_create(request):
    suppliers = PartyRegSupplier.objects.all()
    types = MaterialType.objects.all()

    if request.method == 'POST':
        supplier_id = request.POST.get('mr_supplier')
        type_id = request.POST.get('mr_type')
        name = request.POST.get('mr_material_name')
        details = request.POST.get('mr_material_details')
        buy_price = request.POST.get('mr_buy_price')
        sell_price = request.POST.get('mr_sell_price', '').strip()
        unit_id = int(request.POST.get('unit'))
        
        sell_price = None if sell_price == '' else sell_price
        
        unit = Unit.objects.get(id=unit_id)

        # Optional fields for inventory (adjust as per your form or defaults)
        invoice_id = request.POST.get('mid_invoice_id', 'Initial Purchase')
        buy_quantity = request.POST.get('mid_buy_quentity', 0)
        buy_paid = request.POST.get('mid_buy_paid', 0)

        if name and buy_price and supplier_id:
            material = MaterialRegistration(
                mr_supplier_id=supplier_id,
                mr_type_id=type_id,
                mr_material_name=name,
                mr_material_details=details,
                mr_buy_price=buy_price,
                mr_sell_price=sell_price,
                unit=unit,
                adminid=request.user.id if request.user.is_authenticated else None
            )
            material.save()

            # # Create MaterialInventoryDetail for initial buy
            # inventory_entry = MaterialInventoryDetail(
            #     mid_material=material,
            #     mid_party=material.mr_supplier,
            #     mid_invoice_id=invoice_id,
            #     mid_buy_quentity=buy_quantity,
            #     mid_buy_prices=buy_price,
            #     mid_buy_paid=buy_paid,
            #     mid_deal_type='buy',
            #     mid_entry_by=request.user if request.user.is_authenticated else None,
            #     mid_entry_date=timezone.now()
            # )
            # inventory_entry.save()

            return redirect('material_list')
        else:
            return HttpResponse("Required fields are missing", status=400)

    return render(request, 'backend/material/material_form.html', {
        'suppliers': suppliers,
        'types': types
    })

# Update a material
@login_required
def material_update(request, id):
    material = get_object_or_404(MaterialRegistration, pk=id)
    suppliers = PartyRegSupplier.objects.all()
    types = MaterialType.objects.all()

    if request.method == 'POST':
        material.mr_supplier_id = request.POST.get('mr_supplier')
        material.mr_type_id = request.POST.get('mr_type')
        material.mr_material_name = request.POST.get('mr_material_name')
        material.mr_material_details = request.POST.get('mr_material_details')
        material.mr_buy_price = request.POST.get('mr_buy_price')
        material.mr_sell_price = request.POST.get('mr_sell_price')
        material.adminid = request.user.id if request.user.is_authenticated else None
        material.save()
        return redirect('material_list')

    return render(request, 'backend/material/material_form.html', {
        'material': material,
        'suppliers': suppliers,
        'types': types
    })
@login_required
def material_delete(request, pk):
    material = get_object_or_404(MaterialRegistration, pk=pk)
    material.delete()
    return redirect('material_list')

@login_required
def material_purchase_list(request):
    purchases = MaterialInventoryDetail.objects.select_related(
        'mid_entry_by', 'mid_material'  
    ).all()

    suppliers = PartyRegSupplier.objects.all()
    materials = MaterialRegistration.objects.all()

    return render(request, 'backend/material/material_purchase_list.html', {
        'purchases': purchases,
        'suppliers': suppliers,
        'materials': materials,
    })




@login_required
def material_purchase_create(request):
    suppliers = PartyRegSupplier.objects.all()
    materials = MaterialRegistration.objects.all()

    if request.method == 'POST':
        try:
            supplier_id = request.POST.get('mid_party')
            material_id = request.POST.get('mid_material_id')
            invoice_id = request.POST.get('mid_invoice_id')
            buy_quantity = float(request.POST.get('mid_buy_quentity', 0))
            buy_paid = float(request.POST.get('mid_buy_paid', 0))
            buy_price = float(request.POST.get('mr_buy_price', 0))
            exp_date = request.POST.get('mid_exp_date')
            deal_type = 'buy'

            # Basic validation
            if not (material_id and invoice_id):
                return HttpResponse("Material and Invoice ID are required", status=400)

            # Get the material and supplier
            material = get_object_or_404(MaterialRegistration, id=material_id)
            if not material.mr_supplier:
                return HttpResponse("Selected material has no supplier assigned", status=400)

            # Calculate price: purchase quantity * unit price from material
            calculated_price = buy_quantity * buy_price

            # Create the inventory entry
            MaterialInventoryDetail.objects.create(
                mid_party=supplier_id,
                mid_entry_by=request.user,
                mid_material=material,
                mid_invoice_id=invoice_id,
                mid_buy_quentity=buy_quantity,
                mid_buy_prices=calculated_price,
                mid_buy_paid=buy_paid,
                mid_exp_date=exp_date if exp_date else None,
                mid_entry_date=timezone.now(),
                mid_deal_type=deal_type,
                mid_adminid=request.user.id,
                mid_due_discount=0,
            )
            return redirect('material_purchase_list')

        except Exception as e:
            return HttpResponse(f"Error creating purchase: {str(e)}", status=400)

    return render(request, 'backend/material/material_purchase_form.html', {
        'suppliers': suppliers,
        'materials': materials,
    })

@login_required
def material_purchase_update(request, id):
    purchase = get_object_or_404(MaterialInventoryDetail, pk=id)
    suppliers = PartyRegSupplier.objects.all()
    materials = MaterialRegistration.objects.all()

    if request.method == 'POST':
        try:
            supplier_id = request.POST.get('mid_party')
            material_id = request.POST.get('mid_material_id')
            invoice_id = request.POST.get('mid_invoice_id')

            if not (supplier_id and material_id and invoice_id):
                return HttpResponse("Supplier, Material and Invoice ID are required", status=400)

            material = get_object_or_404(MaterialRegistration, id=material_id)

            # ✅ Save the supplier's ID directly
            purchase.mid_party = supplier_id
            purchase.mid_material = material
            purchase.mid_invoice_id = invoice_id
            purchase.mid_buy_quentity = float(request.POST.get('mid_buy_quentity', 0))
            purchase.mid_buy_prices = float(request.POST.get('mid_buy_prices', 0))
            purchase.mid_buy_paid = float(request.POST.get('mid_buy_paid', 0))
            purchase.mid_exp_date = request.POST.get('mid_exp_date') or None
            purchase.mid_entry_date = timezone.now()
            purchase.mid_adminid = request.user.id
            purchase.save()

            return redirect('material_purchase_list')

        except Exception as e:
            return HttpResponse(f"Error updating purchase: {str(e)}", status=400)

    return render(request, 'backend/material/material_purchase_form.html', {
        'purchase': purchase,
        'suppliers': suppliers,
        'materials': materials,
    })
@login_required
def material_purchase_delete(request, id):  # was: pk
    purchase = get_object_or_404(MaterialInventoryDetail, pk=id)
    try:
        purchase.delete()
        return redirect('material_purchase_list')
    except Exception as e:
        return HttpResponse(f"Error deleting purchase: {str(e)}", status=400)



@login_required
def customer_list(request):
    customers = CustomerInfo.objects.all()
    return render(request, 'backend/customer/customer_list.html', {
        'customers': customers,
    })


@login_required
def customer_create(request):
    if request.method == 'POST':
        try:
            # Auto-generate CustomerID
            last_customer = CustomerInfo.objects.order_by('-id').first()
            if last_customer and last_customer.CustomerID.startswith('CUS-'):
                last_number = int(last_customer.CustomerID.split('-')[1])
            else:
                last_number = 0
            new_customer_id = f"CUS-{last_number + 1:08d}"

            name = request.POST.get('CustomerName')
            address = request.POST.get('CustomerAddress')
            email = request.POST.get('CustomerEmail')
            contact = request.POST.get('CustomerContact')
            reg_date = request.POST.get('RegDate')
            dabite = request.POST.get('dabite')
            cradit = request.POST.get('cradit')
            adminid = request.user.id
            type_ = request.POST.get('type')
            open_due = request.POST.get('open_due')

            if not name:
                return HttpResponse("Customer Name is required", status=400)

            CustomerInfo.objects.create(
                CustomerID=new_customer_id,
                CustomerName=name,
                CustomerAddress=address,
                CustomerEmail=email,
                CustomerContact=contact,
                RegDate=reg_date,
                dabite=dabite,
                cradit=cradit,
                adminid=adminid,
                type=type_,
                open_due=open_due
            )
            return redirect('customer_list')

        except Exception as e:
            return HttpResponse(f"Error creating customer: {str(e)}", status=400)

    return render(request, 'backend/customer/customer_form.html')


@login_required
def customer_update(request, id):
    customer = get_object_or_404(CustomerInfo, pk=id)

    if request.method == 'POST':
        try:
            customer.CustomerID = request.POST.get('CustomerID')
            customer.CustomerName = request.POST.get('CustomerName')
            customer.CustomerAddress = request.POST.get('CustomerAddress')
            customer.CustomerEmail = request.POST.get('CustomerEmail')
            customer.CustomerContact = request.POST.get('CustomerContact')
            customer.RegDate = request.POST.get('RegDate')
            customer.dabite = request.POST.get('dabite')
            customer.cradit = request.POST.get('cradit')
            customer.adminid = request.user.id
            customer.type = request.POST.get('type')
            customer.open_due = request.POST.get('open_due')
            customer.save()

            return redirect('customer_list')

        except Exception as e:
            return HttpResponse(f"Error updating customer: {str(e)}", status=400)

    return render(request, 'backend/customer/customer_form.html', {
        'customer': customer
    })

@login_required
def customer_delete(request, id):
    customer = get_object_or_404(CustomerInfo, pk=id)
    try:
        customer.delete()
        return redirect('customer_list')
    except Exception as e:
        return HttpResponse(f"Error deleting customer: {str(e)}", status=400)




@login_required
# List all warehouses
def warehouse_list(request):
    warehouses = InvWarehouse.objects.all()
    users = User.objects.all()  # Fetch all users
    return render(request, 'backend/warehouse/warehouse_list.html', {
        'warehouses': warehouses,
        'users':users
    })

@login_required
# Create a new warehouse
def warehouse_create(request):
    users = User.objects.all()

    if request.method == 'POST':
        try:
            # Auto-generate Warehouse Code
            last_warehouse = InvWarehouse.objects.order_by('-invw_id').first()
            if last_warehouse and last_warehouse.invw_code.startswith('WH-'):
                last_number = int(last_warehouse.invw_code.split('-')[1])
            else:
                last_number = 0
            new_warehouse_code = f"WH-{last_number + 1:04d}"

            # Get form data
            name = request.POST.get('invw_name')
            address = request.POST.get('invw_address')
            city = request.POST.get('invw_city')
            state = request.POST.get('invw_state')
            postal_code = request.POST.get('invw_postal_code')
            country = request.POST.get('invw_country')
            contact_person = request.POST.get('invw_contact_person')
            contact_phone = request.POST.get('invw_contact_phone')
            contact_email = request.POST.get('invw_contact_email')
            user_id = request.POST.get('invw_user')
            status = request.POST.get('invw_status', 1)

            # Validate required fields
            if not name:
                return HttpResponse("Warehouse name is required", status=400)

            # Get user instance
            try:
                assigned_user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return HttpResponse("Invalid user selected", status=400)
            user = request.user if request.user.is_authenticated else None

            # Create warehouse
            warehouse = InvWarehouse(
                invw_code=new_warehouse_code,
                invw_name=name,
                invw_address=address,
                invw_city=city,
                invw_state=state,
                invw_postal_code=postal_code,
                invw_country=country,
                invw_contact_person=contact_person,
                invw_contact_phone=contact_phone,
                invw_contact_email=contact_email,
                invw_user=assigned_user,
                invw_status=status,
                invw_created_by=user  # Set the creator to current user
            )
            warehouse.save()

            return redirect('warehouse_list')

        except Exception as e:
            return HttpResponse(f"Error creating warehouse: {str(e)}", status=400)

    return render(request, 'backend/warehouse/warehouse_list.html', {
        'users': users
    })

@login_required
def warehouse_update(request, id):
    warehouse = get_object_or_404(InvWarehouse, pk=id)
    users = User.objects.all()

    if request.method == 'POST':
        try:
            # Update warehouse fields
            warehouse.invw_name = request.POST.get('invw_name')
            warehouse.invw_address = request.POST.get('invw_address')
            warehouse.invw_city = request.POST.get('invw_city')
            warehouse.invw_state = request.POST.get('invw_state')
            warehouse.invw_postal_code = request.POST.get('invw_postal_code')
            warehouse.invw_country = request.POST.get('invw_country')
            warehouse.invw_contact_person = request.POST.get('invw_contact_person')
            warehouse.invw_contact_phone = request.POST.get('invw_contact_phone')
            warehouse.invw_contact_email = request.POST.get('invw_contact_email')
            warehouse.invw_status = request.POST.get('invw_status', 1)
            warehouse.invw_updated_by = request.user if request.user.is_authenticated else None

            # Update assigned user
            user_id = request.POST.get('invw_user')
            try:
                assigned_user = User.objects.get(pk=user_id)
                warehouse.invw_user = assigned_user
            except User.DoesNotExist:
                return HttpResponse("Invalid user selected", status=400)
            
            # Set updated by
            
            warehouse.save()

            return redirect('warehouse_list')

        except Exception as e:
            return HttpResponse(f"Error updating warehouse: {str(e)}", status=400)

    return render(request, 'backend/warehouse/warehouse_list.html', {
        'warehouse': warehouse,
        'users': users
    })

@login_required
# Delete a warehouse
def warehouse_delete(request, id):
    try:
        warehouse = get_object_or_404(InvWarehouse, pk=id)
        warehouse.delete()
        return redirect('warehouse_list')
    except Exception as e:
        return HttpResponse(f"Error deleting warehouse: {str(e)}", status=400)
    
    

def inventory_stock_report(request):
    # Annotate total buy and sell quantities
    materials = MaterialRegistration.objects.annotate(
        total_buy=Sum('inventory_entries__mid_buy_quentity'),
        total_sell=Sum('inventory_entries__mid_sell_quentity'),
    ).annotate(
        total_stock=ExpressionWrapper(
            F('total_buy') - F('total_sell'),
            output_field=DecimalField()
        ),
        total_value=ExpressionWrapper(
            F('mr_sell_price') * (F('total_buy') - F('total_sell')),
            output_field=DecimalField()
        )
    ).select_related('mr_type', 'mr_supplier')

    # Apply filters
    material_type = request.GET.get('material_type')
    supplier = request.GET.get('supplier')
    
    if material_type:
        materials = materials.filter(mr_type=material_type)
    if supplier:
        materials = materials.filter(mr_supplier=supplier)

    # Calculate total inventory value
    total_inventory_value = sum([
        material.total_value or 0 for material in materials
    ])

    # CSV export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_stock.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Material', 'Type', 'Supplier', 'Stock', 'Unit Price', 'Value'])
        
        for material in materials:
            writer.writerow([
                material.mr_material_name,
                material.mr_type.TypeName if material.mr_type else '',
                material.mr_supplier.prs_name if material.mr_supplier else '',
                round(material.total_stock or 0, 2),
                round(material.mr_sell_price or 0, 2),
                round(material.total_value or 0, 2),
            ])
        return response

    return render(request, 'backend/reports/inventory_stock.html', {
        'materials': materials,
        'material_types': MaterialType.objects.all(),
        'suppliers': PartyRegSupplier.objects.all(),
        'total_inventory_value': total_inventory_value,
    })
    
    

from django.shortcuts import render
from django.db.models import Sum, F, Q, DecimalField
from django.db.models.functions import Coalesce
from django.db.models.expressions import ExpressionWrapper, Value
from .models import MaterialRegistration, MaterialType, PartyRegSupplier

from django.shortcuts import render
from django.db.models import Sum, F, Q, DecimalField, ExpressionWrapper, Value
from django.db.models.functions import Coalesce

def low_stock_report(request):
    # Default threshold (can be overridden via GET param)
    low_stock_threshold = float(request.GET.get('threshold', 10))

    # Filter parameters
    material_type_id = request.GET.get('material_type')
    supplier_id = request.GET.get('supplier')

    # Start with all materials
    materials = MaterialRegistration.objects.all()

    # Annotate with total bought and sold quantities based on deal type
    decimal_zero = Value(0, output_field=DecimalField(max_digits=20, decimal_places=2))

    materials = materials.annotate(
        total_bought=Coalesce(
            Sum('inventory_entries__mid_buy_quentity',
                filter=Q(inventory_entries__mid_deal_type='buy'),
                output_field=DecimalField(max_digits=20, decimal_places=2)),
            decimal_zero
        ),
        total_sold=Coalesce(
            Sum('inventory_entries__mid_sell_quentity',
                filter=Q(inventory_entries__mid_deal_type='sell'),
                output_field=DecimalField(max_digits=20, decimal_places=2)),
            decimal_zero
        )
    )

    # Annotate current stock and total value
    materials = materials.annotate(
        stock=ExpressionWrapper(
            F('total_bought') - F('total_sold'),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        ),
        total_value=ExpressionWrapper(
            (F('total_bought') - F('total_sold')) * F('mr_sell_price'),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )

    # Filter materials based on low stock threshold
    materials = materials.filter(stock__lte=low_stock_threshold)

    # Apply additional filters if provided
    if material_type_id:
        materials = materials.filter(mr_type_id=material_type_id)
    if supplier_id:
        materials = materials.filter(mr_supplier_id=supplier_id)

    # Calculate total stock of filtered low-stock materials
    total_current_stock = materials.aggregate(
        total_stock_sum=Coalesce(
            Sum('stock', output_field=DecimalField(max_digits=20, decimal_places=2)),
            decimal_zero
        )
    )['total_stock_sum']

    # Get data for filters
    material_types = MaterialType.objects.all()
    suppliers = PartyRegSupplier.objects.all()

    context = {
        'materials': materials,
        'material_types': material_types,
        'suppliers': suppliers,
        'low_stock_threshold': low_stock_threshold,
        'selected_material_type': material_type_id or '',
        'selected_supplier': supplier_id or '',
        'current_stock': total_current_stock,
    }

    return render(request, 'backend/reports/low_stock_report.html', context)


@login_required
def material_transactions_report(request):
    transactions = MaterialInventoryDetail.objects.select_related(
        'mid_material', 'mid_party', 'mid_entry_by'
    ).order_by('-mid_entry_date')

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    material = request.GET.get('material')
    transaction_type = request.GET.get('transaction_type')

    if date_from:
        transactions = transactions.filter(mid_entry_date__gte=date_from)
    if date_to:
        transactions = transactions.filter(mid_entry_date__lte=date_to)
    if material:
        transactions = transactions.filter(mid_material=material)
    if transaction_type:
        transactions = transactions.filter(mid_deal_type=transaction_type)

    # Calculate total_amount for each transaction and store it in a list of dicts
    transactions_with_total = []
    for t in transactions:
        if t.mid_deal_type == 'buy':
            quantity = t.mid_buy_quentity
            price = t.mid_buy_prices
        else:
            quantity = t.mid_sell_quentity
            price = t.mid_sell_prices
        total_amount = quantity * price if quantity and price else 0
        transactions_with_total.append({
            'transaction': t,
            'quantity': quantity,
            'price': price,
            'total_amount': total_amount
        })

    # You can also calculate total quantities and totals here if needed

    return render(request, 'backend/reports/material_transactions.html', {
        'transactions_with_total': transactions_with_total,
        'materials': MaterialRegistration.objects.all(),
        'request': request
    })

@login_required
def sales_report(request):
    orders = Order.objects.select_related('customer').prefetch_related('items__product').order_by('-created_at')

    # Filtering by status and date range
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if status:
        orders = orders.filter(status=status)
    if date_from:
        orders = orders.filter(created_at__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__lte=date_to)

    # Calculate totals per order and overall total sales
    orders_with_totals = []
    total_sales = 0

    for order in orders:
        order_total = sum(item.quantity * item.product.base_price for item in order.items.all())
        total_sales += order_total
        orders_with_totals.append({
            'order': order,
            'total': order_total,
        })

    # Handle CSV export if requested
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Date', 'Customer', 'Status', 'Items', 'Total Price'])

        for entry in orders_with_totals:
            order = entry['order']
            items_str = ', '.join([f"{item.quantity} x {item.product.name}" for item in order.items.all()])
            writer.writerow([
                order.id,
                order.created_at.strftime('%Y-%m-%d'),
                order.customer.name,
                order.get_status_display(),
                items_str,
                f"{entry['total']:.2f}",
            ])

        # Add total sales row
        writer.writerow([])
        writer.writerow(['', '', '', '', 'Total Sales', f"{total_sales:.2f}"])

        return response

    # Render template with calculated totals
    return render(request, 'backend/reports/sales_report.html', {
        'orders_with_totals': orders_with_totals,
        'total_sales': total_sales,
        'status_choices': Order.STATUS_CHOICES,
        'request': request,
    })
    
@login_required
def product_material_usage_report(request):
    products = Product.objects.prefetch_related('productmaterial_set__material')

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="product_material_usage.csv"'

        writer = csv.writer(response)
        writer.writerow(['Product', 'Material', 'Quantity', 'Unit', 'Unit Price', 'Total Cost'])

        for product in products:
            for pm in product.productmaterial_set.all():
                total_cost = pm.quantity * pm.material.unit_price
                writer.writerow([
                    product.name,
                    pm.material.name,
                    pm.quantity,
                    pm.material.measurement_unit.symbol,
                    pm.material.unit_price,
                    total_cost
                ])
        return response

    return render(request, 'backend/reports/product_material_usage.html', {
        'products': products
    })


@login_required
def customer_report(request):
    # Get all customers with optional filters
    customers = CustomerInfo.objects.all().order_by('-RegDate')

    # Apply filters if provided
    customer_type = request.GET.get('type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if customer_type:
        customers = customers.filter(type=customer_type)
    if date_from:
        customers = customers.filter(RegDate__gte=date_from)
    if date_to:
        customers = customers.filter(RegDate__lte=date_to)

    # Get unique customer types for filter dropdown
    customer_types = CustomerInfo.objects.values_list('type', flat=True).distinct()

    # Handle CSV export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customer_report_{}.csv"'.format(
            datetime.now().strftime('%Y-%m-%d')
        )

        writer = csv.writer(response)
        writer.writerow([
            'Customer ID', 'Name', 'Address', 'Email', 'Contact', 
            'Registration Date', 'Debit', 'Credit', 'Type', 'Open Due'
        ])

        for customer in customers:
            writer.writerow([
                customer.CustomerID,
                customer.CustomerName,
                customer.CustomerAddress,
                customer.CustomerEmail,
                customer.CustomerContact,
                customer.RegDate.strftime('%Y-%m-%d'),
                customer.dabite,
                customer.cradit,
                customer.type,
                customer.open_due
            ])

        return response

    context = {
        'customers': customers,
        'customer_types': customer_types,
        'request': request,
    }

    return render(request, 'backend/reports/customer_report.html', context)


@login_required
def profit_loss_report(request):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    date_from = request.GET.get('date_from', start_date.strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))

    try:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        date_from = start_date
        date_to = end_date

    # Revenue
    revenue = MaterialInventoryDetail.objects.filter(
        mid_deal_type='sell',
        mid_entry_date__date__range=[date_from, date_to]
    ).aggregate(
        total_revenue=Sum(
            ExpressionWrapper(
                F('mid_sell_quentity') * F('mid_sell_prices'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        )
    )['total_revenue'] or 0

    # COGS
    cogs = MaterialInventoryDetail.objects.filter(
        mid_deal_type='buy',
        mid_entry_date__date__range=[date_from, date_to]
    ).aggregate(
        total_cogs=Sum(
            ExpressionWrapper(
                F('mid_buy_quentity') * F('mid_buy_prices'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        )
    )['total_cogs'] or 0

    gross_profit = revenue - cogs

    # Expenses
    customer_debits = CustomerInfo.objects.aggregate(
        total=Sum('dabite', output_field=DecimalField(max_digits=20, decimal_places=2))
    )['total'] or 0

    supplier_credits = PartyRegSupplier.objects.aggregate(
        total=Sum('open_sdue', output_field=DecimalField(max_digits=20, decimal_places=2))
    )['total'] or 0

    total_expenses = customer_debits + supplier_credits
    net_profit = gross_profit - total_expenses

    # Monthly trends
    raw_monthly_data = MaterialInventoryDetail.objects.filter(
        mid_entry_date__date__range=[date_from, date_to]
    ).annotate(
        month=TruncMonth('mid_entry_date')
    ).values('month').annotate(
        revenue=Sum(
            ExpressionWrapper(
                F('mid_sell_quentity') * F('mid_sell_prices'),
                output_field=DecimalField()
            ),
            filter=models.Q(mid_deal_type='sell')
        ),
        cogs=Sum(
            ExpressionWrapper(
                F('mid_buy_quentity') * F('mid_buy_prices'),
                output_field=DecimalField()
            ),
            filter=models.Q(mid_deal_type='buy')
        )
    ).order_by('month')

    # Precompute gross profit for each month (so no math in template)
    monthly_data = []
    for row in raw_monthly_data:
        revenue_val = row['revenue'] or 0
        cogs_val = row['cogs'] or 0
        month_gross = revenue_val - cogs_val
        monthly_data.append({
            'month': row['month'],
            'revenue': revenue_val,
            'cogs': cogs_val,
            'gross': month_gross
        })

    # CSV export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="profit_loss_report_{date_from}_{date_to}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Profit & Loss Report', f'{date_from} to {date_to}'])
        writer.writerow([])
        writer.writerow(['Revenue', f'${revenue:.2f}'])
        writer.writerow(['Cost of Goods Sold', f'(${cogs:.2f})'])
        writer.writerow(['Gross Profit', f'${gross_profit:.2f}'])
        writer.writerow(['Expenses', f'(${total_expenses:.2f})'])
        writer.writerow(['Net Profit', f'${net_profit:.2f}'])
        writer.writerow([])
        writer.writerow(['Monthly Trends'])
        writer.writerow(['Month', 'Revenue', 'COGS', 'Gross Profit'])
        for row in monthly_data:
            writer.writerow([
                row['month'].strftime('%B %Y'),
                f'${row["revenue"]:.2f}',
                f'${row["cogs"]:.2f}',
                f'${row["gross"]:.2f}'
            ])
        return response

    context = {
        'date_from': date_from,
        'date_to': date_to,
        'revenue': revenue,
        'cogs': cogs,
        'gross_profit': gross_profit,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'monthly_data': monthly_data,
        'gross_margin': (gross_profit / revenue * 100) if revenue else 0,
        'net_margin': (net_profit / revenue * 100) if revenue else 0,
    }

    return render(request, 'backend/reports/profit_loss_report.html', context)


@login_required
def supplier_detail(request, supplier_id):
    # Get supplier or 404
    supplier = get_object_or_404(PartyRegSupplier, prs_slid=supplier_id)

    # Get inventory details
    inventory_details = MaterialInventoryDetail.objects.filter(mid_party=supplier)

    total_buy = 0
    total_paid = 0

    for item in inventory_details:
        # Check if item has material linked
        if item.mid_material_id is None:
            # No material ID means payment
            item.amount = item.mid_buy_paid or 0
            total_paid += item.amount
            # Mark the deal type explicitly if needed
            item.mid_deal_type = 'payment'
        else:
            # Has material ID, normal buy or sell
            if item.mid_deal_type == 'buy':
                item.amount = item.mid_buy_prices or 0
                total_buy += item.amount
                item.amount = item.mid_buy_paid or 0
                total_paid += item.amount

    net_balance = total_buy - total_paid

    context = {
        'supplier': supplier,
        'inventory_details': inventory_details,
        'total_buy': total_buy,
        'total_sell': total_paid,
        'net_balance': net_balance,
    }

    return render(request, 'backend/party_supplier/supplier_detail.html', context)
@login_required
def blog_banner(request):
    banner = BlogBanner.objects.last()
    if not banner:
        banner = BlogBanner.objects.create()
    if request.method == 'POST':
        form = AboutUsBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog banner updated successfully!')
            return redirect('blog_banner')
    else:
        form = AboutUsBannerForm(instance=banner)
    return render(request, 'backend/Blog/banner.html', {
        'form': form,
        'banner': banner
    })
    
@login_required  
def product_banner(request):
    banner = ProductBanner.objects.last()
    if not banner:
        banner = ProductBanner.objects.create()
    if request.method == 'POST':
        form = AboutUsBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shop  banner updated successfully!')
            return redirect('product_banner')
    else:
        form = AboutUsBannerForm(instance=banner)
    return render(request, 'backend/products/banner.html', {
        'form': form,
        'banner': banner
    })
    
@login_required
def home_CTA(request):
    cta = HomeCTA.objects.first()
    if request.method == "POST":
        form = HomeCallToActionForm(request.POST, request.FILES, instance=cta)
        if form.is_valid():
            form.save()
            return redirect('home_CTA')
    else:
        form = HomeCallToActionForm(instance=cta)
    return render(request, 'backend/home_cta.html', {
        'form': form,
        'cta': cta,
    })
    
    
@login_required 
# Discount Category Views
def discount_category_list(request):
    categories = DiscountCategory.objects.all()
    return render(request, 'backend/discount/category_list.html', {
        'categories': categories
    })
@login_required
def discount_category_create(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            status = int(request.POST.get('status', 1))

            if not (name and start_date and end_date):
                return HttpResponse("Name, start date and end date are required", status=400)

            DiscountCategory.objects.create(
                name=name,
                description=description,
                image=image,
                start_date=start_date,
                end_date=end_date,
                status=status
            )
            return redirect('discount_category_list')
        except Exception as e:
            return HttpResponse(f"Error creating category: {str(e)}", status=400)

    return render(request, 'backend/discount/category_form.html')
@login_required
def discount_category_update(request, pk):
    category = get_object_or_404(DiscountCategory, pk=pk)
    
    if request.method == 'POST':
        try:
            category.name = request.POST.get('name')
            category.description = request.POST.get('description')
            if 'image' in request.FILES:
                category.image = request.FILES['image']
            category.start_date = request.POST.get('start_date')
            category.end_date = request.POST.get('end_date')
            category.status = int(request.POST.get('status', 1))
            category.save()
            return redirect('discount_category_list')
        except Exception as e:
            return HttpResponse(f"Error updating category: {str(e)}", status=400)

    return render(request, 'backend/discount/category_form.html', {
        'category': category
    })
@login_required
def discount_category_delete(request, pk):
    category = get_object_or_404(DiscountCategory, pk=pk)
    try:
        category.delete()
        return redirect('discount_category_list')
    except Exception as e:
        return HttpResponse(f"Error deleting category: {str(e)}", status=400)
@login_required
def discount_list(request):
    discounts = Discount.objects.prefetch_related('products', 'category').all()
    products = Product.objects.all()
    categories = DiscountCategory.objects.all()
    return render(request, 'backend/discount/discount_list.html', {
        'discounts': discounts,
        'products': products,
        'categories': categories,
    })

@login_required
def discount_create(request):
    products = Product.objects.all().order_by('name')
    categories = DiscountCategory.objects.all().order_by('name')

    if request.method == 'POST':
        product_ids = request.POST.getlist('products')
        category_id = request.POST.get('category_id')
        discount_type = request.POST.get('discount_type')
        discount_value = request.POST.get('discount_value')
        status = request.POST.get('status', 1)

        # Check for missing required fields
        missing_fields = []
        if not product_ids:
            missing_fields.append('Products')
        if not category_id:
            missing_fields.append('Category')
        if not discount_type:
            missing_fields.append('Discount Type')
        if not discount_value:
            missing_fields.append('Discount Value')

        if missing_fields:
            messages.error(request, f"The following fields are required: {', '.join(missing_fields)}")
            preserved_data = request.POST.dict()
            preserved_data['products'] = product_ids
            return render(request, 'backend/discount/discount_create.html', {
                'products': products,
                'categories': categories,
                'preserved_data': preserved_data
            })

        try:
            category = DiscountCategory.objects.get(id=category_id)

            # Validate discount value if percentage
            if discount_type == 'percent' and float(discount_value) > 100:
                messages.error(request, 'Percentage discount cannot exceed 100%')
                preserved_data = request.POST.dict()
                preserved_data['products'] = product_ids
                return render(request, 'backend/discount/discount_create.html', {
                    'products': products,
                    'categories': categories,
                    'preserved_data': preserved_data
                })

            discount = Discount.objects.create(
                category=category,
                discount_type=discount_type,
                discount_value=discount_value,
                status=status,
            )

            selected_products = Product.objects.filter(id__in=product_ids)
            discount.products.set(selected_products)

            messages.success(request, f'Discount created successfully for {selected_products.count()} products!')
            return redirect('discount_list')

        except DiscountCategory.DoesNotExist:
            messages.error(request, 'Selected category does not exist')
        except ValueError as e:
            messages.error(request, f'Invalid value: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error creating discount: {str(e)}')

        # Return with preserved data if any error occurs
        preserved_data = request.POST.dict()
        preserved_data['products'] = product_ids
        return render(request, 'backend/discount/discount_create.html', {
            'products': products,
            'categories': categories,
            'preserved_data': preserved_data
        })

    # GET request - render empty form
    return render(request, 'backend/discount/discount_create.html', {
        'products': products,
        'categories': categories,
    })
@login_required
def discount_update(request, discount_id):
    discount = get_object_or_404(Discount, id=discount_id)
    products = Product.objects.all()
    categories = DiscountCategory.objects.all()

    if request.method == 'POST':
        product_ids = request.POST.getlist('products')
        category_id = request.POST.get('category_id')
        discount_type = request.POST.get('discount_type')
        discount_value = request.POST.get('discount_value')
        status = request.POST.get('status', 1)

        try:
            category = DiscountCategory.objects.get(id=category_id)
            discount.category = category
            discount.discount_type = discount_type
            discount.discount_value = discount_value
            discount.status = status
            discount.save()

            selected_products = Product.objects.filter(id__in=product_ids)
            discount.products.set(selected_products)

            messages.success(request, 'Discount updated successfully!')
            return redirect('discount_list')
        except Exception as e:
            messages.error(request, f'Error updating discount: {str(e)}')

    return render(request, 'backend/discount/discount_form.html', {
        'discount': discount,
        'products': products,
        'categories': categories,
    })
@login_required
def discount_delete(request, pk):
    discount = get_object_or_404(Discount, pk=pk)
    try:
        discount.delete()
        messages.success(request, 'Discount deleted successfully!')
        return redirect('discount_list')
    except Exception as e:
        messages.error(request, f'Error deleting discount: {str(e)}')
        return redirect('discount_list')
    
@login_required    
def blog_post(request):
    posts = BlogPost.objects.all().order_by('-id')
    categories = Product.objects.all()  # Using Product as category
    form = BlogPostForm()
    return render(request, 'backend/Blog/post.html', {
        'posts': posts,
        'categories': categories,
        'form': form
    })
@login_required
@require_http_methods(["POST"])
def create_or_update_post(request):
    try:
        post_id = request.POST.get('id')
        
        if post_id and post_id.strip():
            # Update existing post
            instance = get_object_or_404(BlogPost, id=post_id)
            form = BlogPostForm(request.POST, request.FILES, instance=instance)
        else:
            # Create new post
            form = BlogPostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save()
            return JsonResponse({
                'success': True, 
                'message': 'Post saved successfully',
                'post_id': post.id
            })
        else:
            return JsonResponse({
                'success': False, 
                'errors': dict(form.errors),
                'message': 'Form validation failed'
            })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e),
            'message': 'An error occurred while saving the post'
        })
@login_required
def get_post(request, id):
    try:
        post = get_object_or_404(BlogPost, id=id)
        data = {
            'id': post.id,
            'title': post.title,
            'author': post.author,
            'category': post.category.id if post.category else '',
            'description': post.description,
            'is_active': post.is_active,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e),
            'message': 'Failed to retrieve post'
        })
@login_required
@require_http_methods(["POST"])
def delete_post(request, id):
    try:
        post = get_object_or_404(BlogPost, id=id)
        post.delete()
        return JsonResponse({
            'success': True,
            'message': 'Post deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e),
            'message': 'Failed to delete post'
        })
@login_required
@csrf_exempt
def ckeditor_upload(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        upload = request.FILES['upload']
        try:
            import os
            from django.conf import settings
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            import uuid
            
            # Generate unique filename
            file_extension = os.path.splitext(upload.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Save file
            file_path = f"ckeditor_uploads/{unique_filename}"
            saved_path = default_storage.save(file_path, ContentFile(upload.read()))
            
            # Get the URL
            file_url = default_storage.url(saved_path)
            
            return JsonResponse({
                'uploaded': True,
                'url': file_url
            })
        except Exception as e:
            return JsonResponse({
                'uploaded': False,
                'error': {'message': f'Upload failed: {str(e)}'}
            })
    
    return JsonResponse({
        'uploaded': False, 
        'error': {'message': 'No file uploaded'}
    })
    
@login_required
def blog_comments(request):
    comments = BlogComment.objects.select_related('blog').all()
    return render (request,'backend/Blog/comments.html', {'comments': comments})

@login_required
def product_review(request):
    reviews = ProductReview.objects.select_related('product').order_by('-created_at')
    return render(request, 'backend/products/reviews.html', {'reviews': reviews})

@login_required
def daily_sell_report(request):
    # Get date parameters from request (default to today)
    date_str = request.GET.get('date', '')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Calculate previous and next day for navigation
    previous_day = selected_date - timedelta(days=1)
    next_day = selected_date + timedelta(days=1)
    
    # Filter sell transactions for the selected date
    sell_transactions = MaterialInventoryDetail.objects.filter(
        mid_deal_type='sell',
        mid_entry_date__date=selected_date
    ).select_related('mid_material',  'mid_material__unit')
    
    # Annotate each transaction with calculated total and get customer details
    transactions_with_totals = []
    for tx in sell_transactions:
        customer = None
    
        # If mid_party is a string like a customer name, use it directly
        # If it's an ID and you have a Customer model, you can look it up manually
    
        if tx.mid_party:
            # Optional: Try to fetch customer info manually by ID or name
            try:
                customer = CustomerInfo.objects.get(id=tx.mid_party)  # if it's an ID
            except:
                try:
                    customer = CustomerInfo.objects.get(name=tx.mid_party)  # if it's a name
                except CustomerInfo.DoesNotExist:
                    customer = None
    
        tx.total = tx.mid_sell_quentity * tx.mid_sell_prices
        tx.customer_details = customer
        transactions_with_totals.append(tx)
        
    # Calculate summary totals
    total_sell_quantity = sum(tx.mid_sell_quentity for tx in sell_transactions)
    total_sell_amount = sum(tx.total for tx in transactions_with_totals)
    total_sell_paid = sum(tx.mid_sell_paid for tx in sell_transactions)
    outstanding = total_sell_amount - total_sell_paid
    
    # Group by material for summary
    material_summary = {}
    for tx in transactions_with_totals:
        material_key = (tx.mid_material.mr_material_name, tx.mid_material.unit.name if tx.mid_material.unit else '')
        if material_key not in material_summary:
            material_summary[material_key] = {
                'quantity': 0,
                'amount': 0,
                'transactions': 0
            }
        material_summary[material_key]['quantity'] += tx.mid_sell_quentity
        material_summary[material_key]['amount'] += tx.total
        material_summary[material_key]['transactions'] += 1
    
    # Convert material summary to list with calculated averages
    material_summary_list = []
    for (material_name, unit_name), data in material_summary.items():
        material_summary_list.append({
            'material_name': material_name,
            'unit_name': unit_name,
            'total_quantity': data['quantity'],
            'total_amount': data['amount'],
            'avg_price': data['amount'] / data['quantity'] if data['quantity'] else 0,
            'transaction_count': data['transactions']
        })
    
    # Sort material summary by material name
    material_summary_list.sort(key=lambda x: x['material_name'])
    
    # Group by customer for customer summary
    customer_summary = {}
    for tx in transactions_with_totals:
        if tx.customer_details:
            customer_key = (tx.customer_details.CustomerID, tx.customer_details.CustomerName)
            if customer_key not in customer_summary:
                customer_summary[customer_key] = {
                    'quantity': 0,
                    'amount': 0,
                    'transactions': 0,
                    'paid': 0,
                    'customer': tx.customer_details
                }
            customer_summary[customer_key]['quantity'] += tx.mid_sell_quentity
            customer_summary[customer_key]['amount'] += tx.total
            customer_summary[customer_key]['paid'] += tx.mid_sell_paid
            customer_summary[customer_key]['transactions'] += 1
    
    # Convert customer summary to list
    customer_summary_list = []
    for (customer_id, customer_name), data in customer_summary.items():
        customer_summary_list.append({
            'customer_id': customer_id,
            'customer_name': customer_name,
            'total_quantity': data['quantity'],
            'total_amount': data['amount'],
            'total_paid': data['paid'],
            'outstanding': data['amount'] - data['paid'],
            'transaction_count': data['transactions'],
            'customer_details': data['customer']
        })
    
    # Sort customer summary by customer name
    customer_summary_list.sort(key=lambda x: x['customer_name'])
    
    context = {
        'selected_date': selected_date,
        'previous_day': previous_day,
        'next_day': next_day,
        'transactions': transactions_with_totals,
        'material_summary': material_summary_list,
        'customer_summary': customer_summary_list,
        'total_sell_quantity': total_sell_quantity,
        'total_sell_amount': total_sell_amount,
        'total_sell_paid': total_sell_paid,
        'outstanding': outstanding,
    }
    
    return render(request, 'backend/reports/daily_sell_report.html', context)






def daily_purchase_report(request):
    date_str = request.GET.get('date')
    if date_str:
        selected_date = parse_date(date_str)
        if not selected_date:
            selected_date = localtime().date()
    else:
        selected_date = localtime().date()

    previous_day = selected_date - timedelta(days=1)
    next_day = selected_date + timedelta(days=1)

    purchases = MaterialInventoryDetail.objects.filter(
        mid_deal_type='buy',
        mid_entry_date__date=selected_date
    )

    zero_decimal = Value(Decimal('0.00'), output_field=DecimalField())

    # total quantity (Decimal)
    total_quantity = purchases.aggregate(
        total_qty=Coalesce(Sum('mid_buy_quentity'), zero_decimal)
    )['total_qty']

    # total amount (Decimal)
    total_amount = purchases.aggregate(
        total_amt=Coalesce(Sum(
            ExpressionWrapper(
                F('mid_buy_quentity') * F('mid_buy_prices'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        ), zero_decimal)
    )['total_amt']

    # total paid (Decimal)
    total_paid = purchases.aggregate(
        total_paid=Coalesce(Sum('mid_buy_paid'), zero_decimal)
    )['total_paid']

    outstanding = total_amount - total_paid

    # Supplier summary
    # Supplier summary
    supplier_summary = purchases.values('mid_party').annotate(
        transaction_count=Count('id'),
        total_quantity=Coalesce(Sum('mid_buy_quentity'), zero_decimal),
        total_amount=Coalesce(Sum(
            ExpressionWrapper(
                F('mid_buy_quentity') * F('mid_buy_prices'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        ), zero_decimal),
        total_paid=Coalesce(Sum('mid_buy_paid'), zero_decimal),
        outstanding=ExpressionWrapper(
            Coalesce(Sum(
                ExpressionWrapper(
                    F('mid_buy_quentity') * F('mid_buy_prices'),
                    output_field=DecimalField(max_digits=20, decimal_places=2)
                )
            ), zero_decimal) - Coalesce(Sum('mid_buy_paid'), zero_decimal),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    ).order_by('mid_party')

    # Enrich supplier names without FK
    supplier_summary = list(supplier_summary)
    for s in supplier_summary:
        supplier = PartyRegSupplier.objects.filter(prs_slid=s['mid_party']).first()
        s['prs_slid'] = s['mid_party']
        s['prs_name'] = supplier.prs_name if supplier else 'Unknown Supplier'

    # Material summary
    # Material summary (basic aggregation)
    raw_material_summary = purchases.values(
        'mid_material'
    ).annotate(
        total_quantity=Coalesce(Sum('mid_buy_quentity'), zero_decimal),
        total_amount=Coalesce(Sum(
            ExpressionWrapper(
                F('mid_buy_quentity') * F('mid_buy_prices'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        ), zero_decimal),
        avg_price=Coalesce(
            ExpressionWrapper(
                Sum(
                    ExpressionWrapper(
                        F('mid_buy_quentity') * F('mid_buy_prices'),
                        output_field=DecimalField(max_digits=20, decimal_places=2)
                    )
                ) / Sum('mid_buy_quentity'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            ),
            zero_decimal
        ),
        transaction_count=Count('id')
    ).order_by('mid_material')
    
    # Enrich material data manually
    material_summary = []
   
    
    for item in raw_material_summary:
        material_id = item['mid_material']
        material = MaterialRegistration.objects.select_related('unit').filter(id=material_id).first()
    
        item['material_id'] = material_id
        item['material_name'] = material.mr_material_name if material else 'Unknown Material'
        item['unit_name'] = material.unit.name if material and material.unit else 'N/A'
        material_summary.append(item)

    transactions = purchases.select_related('mid_material').order_by('-mid_entry_date')

    context = {
        'selected_date': selected_date,
        'previous_day': previous_day,
        'next_day': next_day,
        'total_purchase_quantity': total_quantity,
        'total_purchase_amount': total_amount,
        'total_purchase_paid': total_paid,
        'outstanding': outstanding,
        'supplier_summary': supplier_summary,
        'material_summary': material_summary,
        'transactions': transactions,
    }
    return render(request, 'backend/reports/daily_purchases_report.html', context)

@login_required
def cart_banner(request):
    banner = CartBanner.objects.last()
    if not banner:
        banner = CartBanner.objects.create()

    if request.method == 'POST':
        form = AboutUsBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cart banner updated successfully!')
            return redirect('cart_banner')
    else:
        form = AboutUsBannerForm(instance=banner)

    return render(request, 'backend/cart/banner.html', {
        'form': form,
        'banner': banner
    })
    
    
    
    
    
    
@login_required
def checkout_banner(request):
    banner = CheckoutBanner.objects.last()
    if not banner:
        banner = CheckoutBanner.objects.create()
    if request.method == 'POST':
        form = AboutUsBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shop  banner updated successfully!')
            return redirect('checkout_banner')
    else:
        form = AboutUsBannerForm(instance=banner)
    return render(request, 'backend/Checkout/banner.html', {
        'form': form,
        'banner': banner
    })
    
@login_required
def order_summary(request):
    orders = OrderSummary.objects.all().order_by('-created_at')  # or filter per user if needed
    context={
        'orders': orders
    }
    return render (request, 'backend/Checkout/orderSummary.html',context)
@login_required
@csrf_exempt  # Optional if using AJAX without CSRF token
def delete_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        try:
            order = OrderSummary.objects.get(order_id=order_id)
            order.delete()
            return JsonResponse({'success': True})
        except OrderSummary.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
@login_required
@csrf_exempt
def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')
        try:
            order = OrderSummary.objects.get(order_id=order_id)
            order.order_status = status
            order.save()
            return JsonResponse({'success': True})
        except OrderSummary.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found.'})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})

@login_required
def supplier_payment(request):
    if request.method == 'POST':
        invoice_id = request.POST.get('invoice_id')
        party_name = request.POST.get('party_name')
        payment_amount_str = request.POST.get('payment_amount')

        try:
            payment_amount = int(payment_amount_str)  # parse as integer
            if payment_amount <= 0:
                raise ValueError("Payment amount must be positive")

            buy_entries = MaterialInventoryDetail.objects.filter(
                mid_invoice_id=invoice_id,
                mid_party=party_name,
                mid_deal_type='buy'
            )

            if not buy_entries.exists():
                messages.error(request, "No matching inventory entries found")
                return redirect('supplier_payment')

            total_price_agg = buy_entries.aggregate(
                total_price=Coalesce(Sum('mid_buy_prices'), Value(0), output_field=IntegerField())
            )
            total_price = total_price_agg['total_price'] or 0

            total_paid_agg = buy_entries.aggregate(  # only 'buy' entries
                total_paid=Coalesce(Sum('mid_buy_paid'), Value(0), output_field=IntegerField())
            )
            total_paid = total_paid_agg['total_paid'] or 0
         
            total_due = total_price - total_paid

            if payment_amount > total_due:
                messages.warning(request, f"Payment amount exceeds total due ({total_due})")
                return redirect('supplier_payment')

            # Create new payment record with mid_deal_type='payment'
            MaterialInventoryDetail.objects.create(
                mid_party=party_name,
                mid_invoice_id=invoice_id,
                mid_buy_paid=payment_amount,
                mid_deal_type='buy',
                # Add other fields if necessary
            )

            messages.success(request, f"Payment of {payment_amount} recorded successfully")
            return redirect('supplier_payment')

        except (ValueError, InvalidOperation) as e:
            messages.error(request, f"Invalid payment amount: {str(e)}")
            return redirect('supplier_payment')

    # GET request - show payment form
    parties_with_due = MaterialInventoryDetail.objects.filter(
        mid_deal_type='buy'
    ).values('mid_party').annotate(
        total_price=Coalesce(Sum('mid_buy_prices'), Value(0), output_field=IntegerField()),
        total_paid=Coalesce(Sum('mid_buy_paid'), Value(0), output_field=IntegerField()),
        total_due=F('total_price') - F('total_paid')
    ).filter(total_due__gt=0)

    context = {
        'parties_with_due': parties_with_due,
    }
    return render(request, 'backend/party_supplier/supplier_payment.html', context)


from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce

@login_required
def get_invoices_for_party(request):
    party_name = request.GET.get('party_name')

    if not party_name:
        return JsonResponse({'invoices': []})

    # Step 1: Aggregate totals with Coalesce to avoid nulls
    invoices_with_due = MaterialInventoryDetail.objects.filter(
        mid_party=party_name,
        mid_deal_type='buy'
    ).values('mid_invoice_id').annotate(
        total_price=Coalesce(Sum('mid_buy_prices'), Value(0, output_field=DecimalField())),
        total_paid=Coalesce(Sum('mid_buy_paid'), Value(0, output_field=DecimalField()))
    )

    # Step 2: Calculate due in Python to avoid ORM arithmetic
    filtered_invoices = []
    for inv in invoices_with_due:
        due = inv['total_price'] - inv['total_paid']
        if due > 0:
            filtered_invoices.append({
                'id': inv['mid_invoice_id'],
                'due': due
            })

    return JsonResponse({'invoices': filtered_invoices})



@login_required
def get_invoice_details(request):
    invoice_id = request.GET.get('invoice_id')
    party_name = request.GET.get('party_name')
    
    if not invoice_id or not party_name:
        return JsonResponse({'details': {}})
    
    invoice_details = MaterialInventoryDetail.objects.filter(
        mid_invoice_id=invoice_id,
        mid_party=party_name,
        mid_deal_type='buy'
    ).aggregate(
        total_amount=Sum('mid_buy_prices'),
        total_paid=Sum('mid_buy_paid'),
    )
    
    total_due = invoice_details['total_amount'] - invoice_details['total_paid']
    
    return JsonResponse({
        'details': {
            'total_amount': invoice_details['total_amount'] or 0,
            'total_paid': invoice_details['total_paid'] or 0,
            'total_due': total_due or 0,
        }
    })
    

@login_required
def invoice_purchase(request, purchase_id):
    purchase = get_object_or_404(MaterialInventoryDetail, id=purchase_id)
    
    # Get supplier details
    supplier = None
    if purchase.mid_party:
        try:
            supplier = PartyRegSupplier.objects.get(prs_slid=purchase.mid_party)
        except PartyRegSupplier.DoesNotExist:
            pass
    
    # Calculate values
    unit_price = purchase.mid_buy_prices / purchase.mid_buy_quentity if purchase.mid_buy_quentity else 0
    balance_due = purchase.mid_buy_prices - purchase.mid_buy_paid
    
    context = {
        'purchase': purchase,
        'supplier': supplier,
        'material': purchase.mid_material,
        'entry_by': purchase.mid_entry_by.get_full_name() if purchase.mid_entry_by else 'System',
        'unit_price': unit_price,
        'balance_due': balance_due,
        'current_date': datetime.now().strftime("%B %d, %Y"),
        'due_date': (purchase.mid_entry_date + timedelta(days=30)).strftime("%B %d, %Y") if purchase.mid_entry_date else "",
    }
    
    return render(request, 'backend/material/invoice_purchase.html', context)

@login_required
def print_invoice_purchase(request, purchase_id):
    purchase = get_object_or_404(MaterialInventoryDetail, id=purchase_id)
    
    # Get supplier details
    supplier = None
    if purchase.mid_party:
        try:
            supplier = PartyRegSupplier.objects.get(prs_slid=purchase.mid_party)
        except PartyRegSupplier.DoesNotExist:
            pass
    
    # Calculate values
    unit_price = purchase.mid_buy_prices / purchase.mid_buy_quentity if purchase.mid_buy_quentity else 0
    balance_due = purchase.mid_buy_prices - purchase.mid_buy_paid
    
    context = {
        'purchase': purchase,
        'supplier': supplier,
        'material': purchase.mid_material,
        'entry_by': purchase.mid_entry_by.get_username() if purchase.mid_entry_by else 'System',
        'unit_price': unit_price,
        'balance_due': balance_due,
        'current_date': datetime.now().strftime("%B %d, %Y"),
        'due_date': (purchase.mid_entry_date + timedelta(days=30)).strftime("%B %d, %Y") if purchase.mid_entry_date else "",
        'print_mode': True,
    }
    
    return render(request, 'backend/material/invoice_purchase.html', context)



@login_required
def search_banner(request):
    banner = SearchViewBanner.objects.last()
    if not banner:
        banner = SearchViewBanner.objects.create()

    if request.method == 'POST':
        form = AboutUsBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'search view page banner updated successfully!')
            return redirect('search_banner')
    else:
        form = AboutUsBannerForm(instance=banner)

    return render(request, 'backend/search/banner.html', {
        'form': form,
        'banner': banner
    })
    
    
@login_required
def thankyou_banner(request):
    banner = ThankyouBanner.objects.last()
    if not banner:
        banner = ThankyouBanner.objects.create()

    if request.method == 'POST':
        form = AboutUsBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'thankyou page banner updated successfully!')
            return redirect('thankyou_banner')
    else:
        form = AboutUsBannerForm(instance=banner)

    return render(request, 'backend/thankyou/banner.html', {
        'form': form,
        'banner': banner
    })