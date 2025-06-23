from django.shortcuts import render
from backend.models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from backend.models import *
from backend.forms import *
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
# Create your views here.



def home(request):
    sliders = HomeSlider.objects.all()
    center_cards = CenterCard.objects.all()
    products = Product.objects.order_by('-created_at')[:8]
    home_cta = HomeCTA.objects.first()
    pricing_card = PricingCard.objects.first()
    brands = Brand.objects.all()
    # Get active parent categories (no parent)
    parent_categories = Category.objects.filter(
        parent_category__isnull=True
    ).order_by('position')[:4]  # Limit to 4 categories
    
    # Prepare category data with their products and product count
    category_data = []
    for category in parent_categories:
        category_products = Product.objects.filter(
            category=category
        ).order_by('-created_at')[:1]  # Get 1 products per category

        product_count = Product.objects.filter(category=category).count()

        if category_products.exists():
            category_data.append({
                'category': category,
                'products': category_products,
                'product_count': product_count,
            })
    
    blogs = BlogPost.objects.filter(is_active=True)
    
    return render(request, 'blue_dot/index.html', {
        'sliders': sliders,
        'center_cards': center_cards,
        'parent_categories': parent_categories,
        'products': products,
        'home_cta': home_cta,
        'pricing_card': pricing_card,
        'category_data': category_data,
        'brands': brands,
        'blogs': blogs
    })






def cart(request):
    banner = CartBanner.objects.last()
    print('banner:',banner)
    cart_items = AddCart.objects.select_related('product').all()

    # Calculate totals in the view
    cart_data = []
    total = 0
    
    for item in cart_items:
        item_total = (item.final_price or 0) * item.quantity

        cart_data.append({
            'item': item,
            'total_cost': item_total
        })
        total += item_total

    context = {
        'banner': banner,
        'cart_data': cart_data,
        'cart_items': cart_items,  # Keep this for backward compatibility
        'subtotal': total,
        'total': total
    }
    return render(request, 'blue_dot/cart.html', context)


def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    quantity = int(request.POST.get('quantity', 1))

    # Ensure session key exists
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    # Get or create cart item filtered by product & session_key
    cart_item, created = AddCart.objects.get_or_create(
        product=product,
        session_key=session_key
    )
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    return redirect('cart')


from django.http import Http404
def remove_from_cart(request, slug):
    """Remove all items for a product from cart"""
    product = get_object_or_404(Product, slug=slug)
    cart_items = AddCart.objects.filter(product=product)

    if not cart_items.exists():
        raise Http404("Cart item not found")

    cart_items.delete()
    return redirect('cart')


@csrf_exempt
def update_cart_quantity(request):
    """Update cart item quantity via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            new_quantity = int(data.get('quantity'))

            if new_quantity <= 0:
                return JsonResponse({'success': False, 'error': 'Quantity must be greater than 0'})

            cart_item = get_object_or_404(AddCart, product_id=product_id)
            cart_item.quantity = new_quantity
            cart_item.save()

            # Safely compute totals
            subtotal = 0
            for item in AddCart.objects.select_related('product').all():
                item_total = (item.final_price or Decimal('0.00')) * item.quantity
                subtotal += item_total

            item_total = (cart_item.final_price or Decimal('0.00')) * cart_item.quantity

            return JsonResponse({
                'success': True,
                'item_total': str(item_total),
                'subtotal': str(subtotal),
                'total': str(subtotal),
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def service(request):
    return render(request, 'blue_dot/service.html')

def service_details(request):
    return render(request, 'blue_dot/service-details.html')



def shop_details(request):
    categories = Category.objects.all()
    print('categories: ', categories)
    context = {
        'categories': categories
    }
    
    return render(request, 'blue_dot/shop-details.html', context)


def blog(request):
    return render(request, 'blue_dot/blog.html')

def blog_details(request):
    return render(request, 'blue_dot/blog-details.html')

def blog_sidebar(request):
    return render(request, 'blue_dot/blog-sideber.html')

def contact(request):
    banner = ContactUsBanner.objects.first()
    locations = ContactLocation.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        number = request.POST.get('number', '').strip()
        website = request.POST.get('website', '').strip()
        message_text = request.POST.get('message', '').strip()

        if name and email and number:
            ContactMessage.objects.create(
                name=name,
                email=email,
                number=number,
                website=website or None,
                message=message_text or ''
            )
            messages.success(request, "Your message has been sent successfully.")
            return redirect('contact')  # or show a thank you page
        else:
            messages.error(request, "Name, Email, and Number are required.")

    return render(request, 'blue_dot/contact.html', {'banner': banner, 'locations': locations,})



def aboutUs(request):
    banner = AboutUsBanner.objects.first()
    about = AboutUs_AboutArea.objects.first()
    cta = CallToAction.objects.first()
    choose_us_section = ChooseUsSection.objects.last()
    choose_us_items = ChooseUsItem.objects.all()  # Fetch all choose us items
    # Add FAQ data
    faq_section = FAQSection.objects.first()
    faq_items = FAQItem.objects.filter(faq_section=faq_section).order_by('id') if faq_section else []
    context = {
        'banner': banner,
        'about': about,
        'cta': cta,
        'choose_us_section': choose_us_section,
        'choose_us_items': choose_us_items,
        'faq_section': faq_section,
        'faq_items': faq_items,
    }
    return render(request, 'blue_dot/about.html', context)




from django.shortcuts import render
from django.db.models import Q, F, Case, When, DecimalField
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
from django.db.models import Min, Max
def shop(request):
    banner = ProductBanner.objects.last()
    categories = Category.objects.all()
    recent_products = Product.objects.order_by('-created_at')[:3]

    products = Product.objects.all()

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Search filter
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    prices = Product.objects.aggregate(min_price=Min('base_price'), max_price=Max('base_price'))
    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price and max_price:
        try:
            min_price = Decimal(min_price)
            max_price = Decimal(max_price)
        except:
            min_price = 0
            max_price = 999999

        # Annotate with product-level discount only
        products = products.annotate(
            calculated_final_price=Case(
                When(discount_type='flat', discount_value__isnull=False,
                     then=F('base_price') - F('discount_value')),
                When(discount_type='percent', discount_value__isnull=False,
                     then=F('base_price') * (1 - F('discount_value') / 100)),
                default=F('base_price'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).filter(
            calculated_final_price__gte=min_price,
            calculated_final_price__lte=max_price
        )

    # Sort options
    sort_option = request.GET.get('sort')
    if sort_option == 'price_asc':
        products = products.order_by('base_price')
    elif sort_option == 'price_desc':
        products = products.order_by('-base_price')
    elif sort_option == 'newest':
        products = products.order_by('-created_at')
    elif sort_option == 'sale':
        products = products.filter(
            Q(discount_type__isnull=False)
        )

    # Pagination
    paginator = Paginator(products.distinct(), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'products': page_obj,
        'recent_products': recent_products,
        'banner': banner,
        'selected_category': category_slug,
        'search_query': search_query or '',
        'min_price': prices['min_price'] or 0,
        'max_price': prices['max_price'] or 10000,
        'sort_option': sort_option or 'default',
    }
    return render(request, 'blue_dot/shop.html', context)


def product_detail(request, slug):
    banner=ProductBanner.objects.last()
    product = get_object_or_404(Product, slug=slug)
    
    # Get the full URL for sharing
    product_url = request.build_absolute_uri()
    
    
    return render(request, 'blue_dot/shop-details.html', {'product': product,'banner':banner,'product_url': product_url,})

def ourteam(request):
    return render(request, 'blue_dot/team.html')

def team_details(request):
    return render(request, 'blue_dot/team-details.html')

def testimonial(request):
    return render(request, 'blue_dot/testimonials.html')

def pricing(request):
    return render(request, 'blue_dot/pricing.html')

def project(request):
    return render(request, 'blue_dot/project.html')

def project_details(request):
    return render(request, 'blue_dot/project-details.html')

def faq(request):
    banner = OurfaqBanner.objects.first()
    faqs = FAQ.objects.filter(is_active=True).order_by('order', '-created_at')
    context = {
        'banner': banner,
        'faqs': faqs,
        
    }
    return render(request, 'blue_dot/faq.html', context)

def error(request):
    return render(request, 'blue_dot/error.html')


def promotion(request):
    now = timezone.now()
    banner=ProductBanner.objects.last()
    categories = DiscountCategory.objects.filter(
        status=1,
        start_date__lte=now,
        end_date__gte=now
    ).order_by('name')
    return render(request, 'blue_dot/discount.html', {
        'categories': categories,
        'current_date': now,
        'banner':banner
    })

def category_products(request, slug):
    # Get the DiscountCategory by slug
    discount_category = get_object_or_404(DiscountCategory, slug=slug)
    category_obj = Category.objects.all()
    banner = ProductBanner.objects.last()

    # Get all discounts for this category
    discounts = Discount.objects.filter(category=discount_category, status=1).prefetch_related('products')

    # Collect products from all related discounts
    products = Product.objects.filter(discounts__in=discounts).distinct().select_related('category', 'brand')
    
    recent_products = Product.objects.order_by('-created_at')[:3]

    # -- Filters below (keep as is or adjust accordingly) --
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    prices = products.aggregate(min_price=Min('base_price'), max_price=Max('base_price'))

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        try:
            min_price = Decimal(min_price)
            max_price = Decimal(max_price)
        except:
            min_price = 0
            max_price = 999999

        products = products.annotate(
            calculated_final_price=Case(
                When(discount_type='flat', discount_value__isnull=False,
                     then=F('base_price') - F('discount_value')),
                When(discount_type='percent', discount_value__isnull=False,
                     then=F('base_price') * (1 - F('discount_value') / 100)),
                default=F('base_price'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).filter(
            calculated_final_price__gte=min_price,
            calculated_final_price__lte=max_price
        )

    sort_option = request.GET.get('sort')
    if sort_option == 'price_asc':
        products = products.order_by('base_price')
    elif sort_option == 'price_desc':
        products = products.order_by('-base_price')
    elif sort_option == 'newest':
        products = products.order_by('-created_at')
    elif sort_option == 'sale':
        products = products.filter(Q(discount_type__isnull=False))

    paginator = Paginator(products.distinct(), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blue_dot/category_products.html', {
        'category': discount_category,
        'products': page_obj,
        'category_obj': category_obj,
        'recent_products': recent_products,
        'banner': banner,
        'selected_category': category_slug,
        'search_query': search_query or '',
        'min_price': prices['min_price'] or 0,
        'max_price': prices['max_price'] or 10000,
        'sort_option': sort_option or 'default',
    })
    


def blog(request):
    banner = BlogBanner.objects.last()
    blogs = BlogPost.objects.filter(is_active=True)
    context={
        'banner':banner,
        'blogs':blogs
    }
    return render(request, 'blue_dot/blog.html',context)

def blog_details(request, slug):
    banner = BlogBanner.objects.last()
    blog = get_object_or_404(BlogPost, slug=slug, is_active=True)
    recent_blogs = BlogPost.objects.order_by('-created_at')[:3]

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email', '')
        number = request.POST.get('number', '')
        message = request.POST.get('message')

        if name and message:
            BlogComment.objects.create(
                blog=blog,
                name=name,
                email=email,
                number=number,
                message=message
            )
            messages.success(request, "Your comment has been submitted successfully.")
            return redirect('blog_details', slug=slug)
        else:
            messages.error(request, "Name and Message are required.")

    comments = blog.comments.all()

    context = {
        'banner': banner,
        'blog': blog,
        'recent_blogs': recent_blogs,
        'comments': comments,
    }
    return render(request, 'blue_dot/blog-details.html',context)


def product_detail(request, slug):
    banner=ProductBanner.objects.last()
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.order_by('-created_at')  # all reviews related to this product

    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.save()
            return redirect('product_detail', slug=product.slug)
    else:
        form = ProductReviewForm()
    return render(request, 'blue_dot/shop-details.html', {'product': product,'banner':banner,'reviews': reviews,'form': form,})








from decimal import Decimal
from django.utils.crypto import get_random_string


from decimal import Decimal
from datetime import date


def cart_checkout(request):
    banner = CheckoutBanner.objects.last()

    # 1. Build cart items
    if 'buy_now_product' in request.session:
        buy_now_data = request.session['buy_now_product']
        from types import SimpleNamespace
        fake_cart_item = SimpleNamespace()
        fake_cart_item.product = get_object_or_404(Product, id=buy_now_data['product_id'])
        fake_cart_item.quantity = buy_now_data['quantity']
        fake_cart_item.final_price = Decimal(str(buy_now_data['unit_price']))
        cart_items = [fake_cart_item]
        is_buy_now = True
    else:
        cart_items = AddCart.objects.select_related('product').all()
        is_buy_now = False

    # 2. Fetch shipping options (district=None = default rates)
    shipping_options = []
    shipping_costs = ShippingCost.objects.filter().select_related('shipping_type')
    for cost in shipping_costs:
        shipping_options.append({
            'id': f"shipping_type_{cost.shipping_type.id}",
            'code': cost.shipping_type.code,
            'name': cost.shipping_type.name,
            'value': cost.cost,
        })

    # 3. Handle form POST
    if request.method == 'POST':
        phone = request.POST.get('phone')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        district_value = request.POST.get('district')  # format: "15-Dhaka"
        thana_value = request.POST.get('thana')        # format: "21-Gulshan"
        address = request.POST.get('address')
        order_notes = request.POST.get('order_notes', '')

        # Extract district/thana names
        district_id, district_name = district_value.split('-', 1) if district_value else ("", "")
        thana_id, thana_name = thana_value.split('-', 1) if thana_value else ("", "")

        # Determine selected shipping
        shipping_cost = Decimal(request.POST.get('shipping_method', '0'))  # Changed from 'shipping' to 'shipping_method'
        selected_option = next((opt for opt in shipping_options if str(opt['value']) == str(shipping_cost)), None)
        shipping_type_code = selected_option['code'] if selected_option else 'unknown'
        shipping_type_name = selected_option['name'] if selected_option else 'Unknown'

        # Calculate totals
        subtotal = sum((item.final_price or 0) * item.quantity for item in cart_items)
        total_amount = subtotal + shipping_cost

        # Save customer
        customer = CustomerInfo.objects.create(
            CustomerID=f"CUST{phone[-4:]}{CustomerInfo.objects.count() + 1}",
            CustomerName=f"{first_name} {last_name}",
            CustomerAddress=f"{district_name} | {thana_name} | {address}",
            CustomerEmail=None,
            CustomerContact=phone,
            district_id=district_id,
            district_name=district_name,
            thana_id=thana_id,
            thana_name=thana_name,
            RegDate=date.today(),
            dabite="0", cradit="0", adminid=None, type="general", open_due="0"
        )

        # Save order
        order = Order.objects.create(
            customer=customer,
            status=5,
            payment_status='pending',
            order_date=date.today(),
            notes=order_notes,
            subtotal=subtotal,
            shipping_type_code=shipping_type_code,  # Store shipping type code
            shipping_type_name=shipping_type_name,  # Store shipping type name
            shipping_cost=shipping_cost,
            total_amount=total_amount
        )

        # Save items
        for item in cart_items:
            product = item.product
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                quantity=item.quantity,
                unit_price=item.final_price or product.final_price or product.base_price,
                total_price=(item.final_price or product.final_price or product.base_price) * item.quantity,
                notes=""
            )

        # Clear cart
        if is_buy_now:
            del request.session['buy_now_product']
        else:
            AddCart.objects.all().delete()

        return redirect('thank_you')

    # 4. Render cart page (GET)
    cart_data = []
    total = 0
    for item in cart_items:
        item_total = (item.final_price or 0) * item.quantity
        cart_data.append({'item': item, 'total_cost': item_total})
        total += item_total

    context = {
        'banner': banner,
        'cart_data': cart_data,
        'cart_items': cart_items,
        'subtotal': total,
        'total': total + (shipping_options[0]['value'] if shipping_options else Decimal('0.00')),
        'shipping_options': shipping_options,
        'is_buy_now': is_buy_now,
    }
    return render(request, 'blue_dot/checkout.html', context)

def get_shipping_options(request):
    district_name = request.GET.get('district', '').strip()
    
    print(f"Received district: '{district_name}'")  # Debug line - remove in production
    
    shipping_costs = ShippingCost.objects.none()

    if district_name:
        # Try multiple approaches to find shipping costs
        # 1. Exact match (case-insensitive)
        shipping_costs = ShippingCost.objects.filter(district__iexact=district_name).select_related('shipping_type')
        
        # 2. If no exact match, try partial match
        if not shipping_costs.exists():
            shipping_costs = ShippingCost.objects.filter(district__icontains=district_name).select_related('shipping_type')
        
        # 3. If still no match, try removing common variations
        if not shipping_costs.exists():
            # Remove common suffixes/prefixes
            clean_name = district_name.replace(' District', '').replace('District', '').strip()
            shipping_costs = ShippingCost.objects.filter(district__icontains=clean_name).select_related('shipping_type')

    # Fallback: get default shipping cost (where district is NULL)
    if not shipping_costs.exists():
        shipping_costs = ShippingCost.objects.filter(district__isnull=True).select_related('shipping_type')
        print("Using default shipping costs")  # Debug line - remove in production

    data = []
    for sc in shipping_costs:
        data.append({
            "id": f"shipping_type_{sc.shipping_type.id}",
            "name": sc.shipping_type.name,
            "code": sc.shipping_type.code,
            "cost": str(sc.cost),
        })
    
    print(f"Returning {len(data)} shipping options")  # Debug line - remove in production
    return JsonResponse({"shipping_options": data})




def thank_you(request):
    banner = ThankyouBanner.objects.last()
    return render(request, 'blue_dot/thankyou.html',{'banner':banner})






from django.db.models import Q

def search_view(request):
    banner = SearchViewBanner.objects.last()
    query = request.GET.get('q')
    results = []
    recent_products = Product.objects.order_by('-created_at')[:3]
    parent_categories = Category.objects.filter(
        parent_category__isnull=True
    ).order_by('position')[:4]

    center_cards = CenterCard.objects.all()
    products = Product.objects.all()

    # Get global price range
    prices = Product.objects.aggregate(
        min_price=Min('base_price'), max_price=Max('base_price')
    )

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price and max_price:
        try:
            min_price = Decimal(min_price)
            max_price = Decimal(max_price)
        except:
            min_price = Decimal(0)
            max_price = Decimal(999999)

        products = products.annotate(
            calculated_final_price=Case(
                When(discount_type='flat', discount_value__isnull=False,
                     then=F('base_price') - F('discount_value')),
                When(discount_type='percent', discount_value__isnull=False,
                     then=F('base_price') * (1 - F('discount_value') / 100)),
                default=F('base_price'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).filter(
            calculated_final_price__gte=min_price,
            calculated_final_price__lte=max_price
        )

    # Sorting
    sort_option = request.GET.get('sort')
    if sort_option == 'price_asc':
        products = products.order_by('base_price')
    elif sort_option == 'price_desc':
        products = products.order_by('-base_price')
    elif sort_option == 'newest':
        products = products.order_by('-created_at')
    elif sort_option == 'sale':
        products = products.filter(discount_type__isnull=False)

    # Apply distinct before pagination
    products = products.distinct()

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    home_cta = HomeCTA.objects.first()
    pricing_card = PricingCard.objects.first()
    brands = Brand.objects.all()

    # Prepare category data with sample product and count
    category_data = []
    for category in parent_categories:
        category_products = Product.objects.filter(
            category=category
        ).order_by('-created_at')[:1]

        product_count = Product.objects.filter(category=category).count()

        if category_products.exists():
            category_data.append({
                'category': category,
                'products': category_products,
                'product_count': product_count,
            })

    # If there's a search query
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

    return render(request, 'blue_dot/search_results.html', {
        'query': query,
        'results': results,
        'parent_categories': parent_categories,
         'recent_products': recent_products,
        'products': page_obj,
        'home_cta': home_cta,
        'pricing_card': pricing_card,
        'category_data': category_data,
        'brands': brands,
        'min_price': prices['min_price'] or 0,
        'max_price': prices['max_price'] or 10000,
        'sort_option': sort_option or 'default',
        'banner':banner,
    })

def buy_now(request, slug):
    """Handle Buy Now - bypass cart and go directly to checkout"""
    if request.method == 'POST':
        product = get_object_or_404(Product, slug=slug)
        quantity = int(request.POST.get('quantity', 1))
        
        # Store buy now data in session
        request.session['buy_now_product'] = {
            'product_id': product.id,
            'product_name': product.name,
            'quantity': quantity,
            'unit_price': float(product.final_price or product.base_price),
            'total_price': float((product.final_price or product.base_price) * quantity),
            'product_slug': product.slug,
        }
        
        # Redirect to checkout
        return redirect('cart_checkout')
    
    # If GET request, redirect to product detail
    return redirect('product_detail', slug=slug)
    
    
    
def machine_list(request):
    machines = Machine.objects.filter(m_status=True)
    banner = MachineBanner.objects.first()  # Get the first banner without is_active filter
    
    return render(request, 'blue_dot/machine_list.html', {
        'machines': machines,
        'banner': banner
    })


def machine_detail(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    details = machine.details.first()  # Related details, if any
    images = machine.images.all()      # Related images
    banner = MachineBanner.objects.first()  # Get the first banner without is_active filter
    
    return render(request, 'blue_dot/machine_detail.html', {
        'machine': machine,
        'details': details,
        'images': images,
        'banner': banner
    })
