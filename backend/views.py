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
    
    user_type = 2
    
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
                status='pending',
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
    return render(request, 'backend/orders/approve_order.html', context)


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


def approve_order(request, id):
    order = Order.objects.filter(id=id).first()
    if not order:
        messages.error(request, 'Order not found.')
        return redirect('order_list')

    customers = CustomerInfo.objects.all()
    products = Product.objects.all()
    materials = MaterialRegistration.objects.all()
    units = Unit.objects.all()
    order_items = order.items.all()

    if request.method == 'POST':
        try:
            with transaction.atomic():
                customer_id = request.POST.get('customer')
                product_id = request.POST.get('product_id')
                order_date = request.POST.get('order_date')
                notes = request.POST.get('notes', '')
                materials_ids = request.POST.getlist('materials[]')
                units_ids = request.POST.getlist('units[]')
                quantities = request.POST.getlist('quantities[]')

                # Validation
                if not customer_id or not product_id:
                    messages.error(request, "Customer and Product are required.")
                    raise ValueError("Missing customer/product.")

                if not materials_ids:
                    messages.error(request, "At least one material is required.")
                    raise ValueError("Missing materials.")

                if len(materials_ids) != len(units_ids) or len(materials_ids) != len(quantities):
                    messages.error(request, "Each material must have corresponding unit and quantity.")
                    raise ValueError("Material/Unit/Quantity mismatch.")

                customer = CustomerInfo.objects.filter(id=customer_id).first()
                product = Product.objects.filter(id=product_id).first()

                if not customer or not product:
                    messages.error(request, "Invalid customer or product.")
                    raise ValueError("Invalid customer/product.")

                # Update order
                order.customer = customer
                order.notes = notes
                order.order_date = order_date
                order.status = '1'  # Approved
                order.save()

                # Remove previous OrderItems and MaterialUsage
                order.items.all().delete()
                MaterialUsage.objects.filter(order=order).delete()

                # Add new OrderItem
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=1
                )

                # Add Material Usages
                for material_id, unit_id, qty in zip(materials_ids, units_ids, quantities):
                    if not qty or float(qty) <= 0:
                        messages.warning(request, f"Skipped material ID {material_id} due to invalid quantity.")
                        continue

                    material = MaterialRegistration.objects.filter(id=material_id).first()
                    unit = Unit.objects.filter(id=unit_id).first()

                    if not material or not unit:
                        messages.warning(request, f"Invalid material or unit for ID {material_id}, {unit_id}. Skipped.")
                        continue

                    MaterialUsage.objects.create(
                        order=order,
                        material=material,
                        unit=unit,
                        quantity_used=qty
                    )

                    InventoryLog.objects.create(
                        material=material,
                        change_type='out',
                        quantity_changed=qty,
                        reference=f"Order #{order.id}"
                    )

                messages.success(request, "Order approved and updated successfully.")
                return redirect('order_list')

        except Exception as e:
            messages.error(request, f"Error approving order: {str(e)}")

    context = {
        'order': order,
        'customers': customers,
        'products': products,
        'materials': materials,
        'units': units,
        'order_items': order_items,
    }
    return render(request, 'backend/orders/approve_order.html', context)



def product_list(request):
    return render(request, 'backend/product-list.html')

def add_product(request):
    return render(request, 'backend/product-add.html')


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


def category_list(request):
    categories = Category.objects.all().order_by('-created_at')
    
    context = {
        'categories': categories,
    }

    return render(request, 'backend/categories/category_list.html', context)


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
    
    

def delete_category(request, pk):
    if request.method == "POST":
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return redirect('category_list')
    
    
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
    
    
# List brands (returns HTML)
@require_http_methods(["GET"])
def brand_list(request):
    brands = Brand.objects.filter(status=1)  # Only active brands
    return render(request, 'backend/brand/index.html', {'brands': brands})

# Create brand (returns JSON)
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
    

def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    
    context = {
        'products': products,
    }
    return render(request, 'backend/products/product_list.html', context)

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



def party_supplier_list(request):
    # List all suppliers (returns HTML)
    suppliers = PartyRegSupplier.objects.all()
    context = {'suppliers': suppliers}
    return render(request, 'backend/party_supplier/list.html', context)

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
def party_supplier_delete(request, slid):
    # Delete a supplier (returns JSON)
    supplier = get_object_or_404(PartyRegSupplier, prs_slid=slid)
    try:
        supplier.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    




# List all material types
def material_type_list(request):
    material_types = MaterialType.objects.all()
    return render(request, 'backend/material/type/type_list.html', {'material_types': material_types})

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

# Delete a material type
@require_http_methods(["POST"])
def material_type_delete(request, pk):
    material_type = get_object_or_404(MaterialType, pk=pk)
    material_type.delete()
    return redirect('material_type_list')





def material_list(request):
    materials = MaterialRegistration.objects.select_related('mr_supplier', 'mr_type').all()
    suppliers = PartyRegSupplier.objects.all()
    types = MaterialType.objects.all()
    units = Unit.objects.all()
    
    return render(request, 'backend/material/material_list.html', {
        'materials': materials,
        'suppliers': suppliers,
        'types': types,
        'units': units,
    })
# Create a new material

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

            # Create MaterialInventoryDetail for initial buy
            inventory_entry = MaterialInventoryDetail(
                mid_material=material,
                mid_party=material.mr_supplier,
                mid_invoice_id=invoice_id,
                mid_buy_quentity=buy_quantity,
                mid_buy_prices=buy_price,
                mid_buy_paid=buy_paid,
                mid_deal_type='buy',
                mid_entry_by=request.user if request.user.is_authenticated else None,
                mid_entry_date=timezone.now()
            )
            inventory_entry.save()

            return redirect('material_list')
        else:
            return HttpResponse("Required fields are missing", status=400)

    return render(request, 'backend/material/material_form.html', {
        'suppliers': suppliers,
        'types': types
    })

# Update a material

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

def material_delete(request, pk):
    material = get_object_or_404(MaterialRegistration, pk=pk)
    material.delete()
    return redirect('material_list')


def material_purchase_list(request):
    purchases = MaterialInventoryDetail.objects.select_related(
        'mid_party', 'mid_entry_by', 'mid_material'
    ).all()

    suppliers = PartyRegSupplier.objects.all()
    materials = MaterialRegistration.objects.all()

    return render(request, 'backend/material/material_purchase_list.html', {
        'purchases': purchases,
        'suppliers': suppliers,
        'materials': materials,
    })





def material_purchase_create(request):
    suppliers = PartyRegSupplier.objects.all()
    materials = MaterialRegistration.objects.all()

    if request.method == 'POST':
        try:
            material_id = request.POST.get('mid_material_id')
            invoice_id = request.POST.get('mid_invoice_id')
            buy_quantity = request.POST.get('mid_buy_quentity', 0)
            buy_price = request.POST.get('mid_buy_prices', 0)
            buy_paid = request.POST.get('mid_buy_paid', 0)
            exp_date = request.POST.get('mid_exp_date')
            deal_type = 'buy'

            # Basic validation
            if not (material_id and invoice_id):
                return HttpResponse("Material and Invoice ID are required", status=400)

            # Get the material and supplier
            material = get_object_or_404(MaterialRegistration, id=material_id)
            if not material.mr_supplier:
                return HttpResponse("Selected material has no supplier assigned", status=400)

            # Create the inventory entry
            MaterialInventoryDetail.objects.create(
                mid_party=material.mr_supplier,
                mid_entry_by=request.user,
                mid_material=material,
                mid_invoice_id=invoice_id,
                mid_buy_quentity=float(buy_quantity),
                mid_buy_prices=float(buy_price),
                mid_buy_paid=float(buy_paid),
                mid_exp_date=exp_date if exp_date else None,
                mid_entry_date=timezone.now(),
                mid_deal_type=deal_type,
                adminid=request.user.id,
                due_discount=0,
            )
            return redirect('material_purchase_list')

        except Exception as e:
            return HttpResponse(f"Error creating purchase: {str(e)}", status=400)

    return render(request, 'backend/material/material_purchase_form.html', {
        'suppliers': suppliers,
        'materials': materials,
    })

def material_purchase_update(request, id):
    purchase = get_object_or_404(MaterialInventoryDetail, pk=id)
    suppliers = PartyRegSupplier.objects.all()
    materials = MaterialRegistration.objects.all()

    if request.method == 'POST':
        try:
            material_id = request.POST.get('mid_material_id')
            invoice_id = request.POST.get('mid_invoice_id')
            
            # Validate required fields
            if not (material_id and invoice_id):
                return HttpResponse("Material and Invoice ID are required", status=400)

            material = get_object_or_404(MaterialRegistration, id=material_id)
            if not material.mr_supplier:
                return HttpResponse("Selected material has no supplier assigned", status=400)

            # Update purchase record
            purchase.mid_party = material.mr_supplier
            purchase.mid_material = material
            purchase.mid_invoice_id = invoice_id
            purchase.mid_buy_quentity = float(request.POST.get('mid_buy_quentity', 0))
            purchase.mid_buy_prices = float(request.POST.get('mid_buy_prices', 0))
            purchase.mid_buy_paid = float(request.POST.get('mid_buy_paid', 0))
            purchase.mid_exp_date = request.POST.get('mid_exp_date') or None
            purchase.mid_entry_date = timezone.now()
            purchase.adminid = request.user.id
            purchase.save()
            
            return redirect('material_purchase_list')

        except Exception as e:
            return HttpResponse(f"Error updating purchase: {str(e)}", status=400)

    return render(request, 'backend/material/material_purchase_form.html', {
        'purchase': purchase,
        'suppliers': suppliers,
        'materials': materials,
    })

def material_purchase_delete(request, pk):
    purchase = get_object_or_404(MaterialInventoryDetail, pk=pk)
    try:
        purchase.delete()
        return redirect('material_purchase_list')
    except Exception as e:
        return HttpResponse(f"Error deleting purchase: {str(e)}", status=400)



def customer_list(request):
    customers = CustomerInfo.objects.all()
    return render(request, 'backend/customer/customer_list.html', {
        'customers': customers,
    })



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


def customer_delete(request, id):
    customer = get_object_or_404(CustomerInfo, pk=id)
    try:
        customer.delete()
        return redirect('customer_list')
    except Exception as e:
        return HttpResponse(f"Error deleting customer: {str(e)}", status=400)





# List all warehouses
def warehouse_list(request):
    warehouses = InvWarehouse.objects.all()
    users = User.objects.all()  # Fetch all users
    return render(request, 'backend/warehouse/warehouse_list.html', {
        'warehouses': warehouses,
        'users':users
    })


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



def supplier_detail(request, supplier_id):
    # Get the supplier or return 404 if not found
    supplier = get_object_or_404(PartyRegSupplier, prs_slid=supplier_id)
    
    # Get all inventory details related to this supplier
    inventory_details = MaterialInventoryDetail.objects.filter(mid_party=supplier).select_related(
        'mid_material', 'mid_entry_by'
    ).order_by('-mid_entry_date')
    
    # Calculate totals
    total_buy = sum(item.mid_buy_quentity * item.mid_buy_prices for item in inventory_details if item.mid_deal_type == 'buy')
    total_sell = sum(item.mid_sell_quentity * item.mid_sell_prices for item in inventory_details if item.mid_deal_type == 'sell')
    
    context = {
        'supplier': supplier,
        'inventory_details': inventory_details,
        'total_buy': total_buy,
        'total_sell': total_sell,
        'net_balance': total_buy - total_sell,
    }
    
    return render(request, 'backend/party_supplier/supplier_detail.html', context)


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
    
    
    
# Discount Category Views
def discount_category_list(request):
    categories = DiscountCategory.objects.all()
    return render(request, 'backend/discount/category_list.html', {
        'categories': categories
    })

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

def discount_category_delete(request, pk):
    category = get_object_or_404(DiscountCategory, pk=pk)
    try:
        category.delete()
        return redirect('discount_category_list')
    except Exception as e:
        return HttpResponse(f"Error deleting category: {str(e)}", status=400)

def discount_list(request):
    discounts = Discount.objects.prefetch_related('products', 'category').all()
    products = Product.objects.all()
    categories = DiscountCategory.objects.all()
    return render(request, 'backend/discount/discount_list.html', {
        'discounts': discounts,
        'products': products,
        'categories': categories,
    })


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

def discount_delete(request, pk):
    discount = get_object_or_404(Discount, pk=pk)
    try:
        discount.delete()
        messages.success(request, 'Discount deleted successfully!')
        return redirect('discount_list')
    except Exception as e:
        messages.error(request, f'Error deleting discount: {str(e)}')
        return redirect('discount_list')
    
    

def blog_post(request):
    posts = BlogPost.objects.all().order_by('-id')  # Order by newest first
    # Get categories instead of products for the dropdown
    categories = Category.objects.all()  # Assuming you have a Category model
    form = BlogPostForm()
    return render(request, 'backend/Blog/post.html', {
        'posts': posts,
        'categories': categories,  # Changed from 'products' to 'categories'
        'form': form
    })

@require_http_methods(["POST"])
def create_or_update_post(request):
    try:
        post_id = request.POST.get('id')
        
        if post_id:
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
                'errors': form.errors,
                'message': 'Form validation failed'
            })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e),
            'message': 'An error occurred while saving the post'
        })

def get_post(request, id):
    try:
        post = get_object_or_404(BlogPost, id=id)
        data = {
            'id': post.id,
            'title': post.title,
            'author': post.author,
            'category': post.category.id,  # Send category ID for the select dropdown
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

# CKEditor image upload handler
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
            
            # Generate unique filename to avoid conflicts
            file_extension = os.path.splitext(upload.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Save file using Django's default storage
            file_path = f"ckeditor_uploads/{unique_filename}"
            saved_path = default_storage.save(file_path, ContentFile(upload.read()))
            
            # Get the URL for the saved file
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
    
def blog_comments(request):
    comments = BlogComment.objects.select_related('blog').all()
    return render (request,'backend/Blog/comments.html', {'comments': comments})


def product_review(request):
    reviews = ProductReview.objects.select_related('product').order_by('-created_at')
    return render(request, 'backend/products/reviews.html', {'reviews': reviews})



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
   