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

    cart_item, created = AddCart.objects.get_or_create(product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    return redirect('cart')


def remove_from_cart(request, slug):
    """Remove item completely from cart"""
    product = get_object_or_404(Product, slug=slug)
    cart_item = get_object_or_404(AddCart, product=product)
    cart_item.delete()
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
    return render(request, 'blue_dot/shop-details.html', {'product': product,'banner':banner})

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
    # Get the selected category by slug
    category = get_object_or_404(Category, slug=slug)

    # Include this category and all its subcategories
    categories = Category.objects.filter(Q(id=category.id) | Q(parent_category=category))

    # Get all products in these categories
    products = Product.objects.filter(category__in=categories).select_related('category', 'brand')

    return render(request, 'blue_dot/category_products.html', {
        'category': category,
        'products': products,
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
    
    # Check if this is a buy now checkout
    if 'buy_now_product' in request.session:
        buy_now_data = request.session['buy_now_product']
        
        # Create a fake cart item for buy now
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

    if request.method == 'POST':
        # Step 1: Extract form data
        phone = request.POST.get('phone')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        district_value = request.POST.get('district')  # format: "15-Dhaka"
        thana_value = request.POST.get('thana')        # format: "21-Gulshan"
        address = request.POST.get('address')
        order_notes = request.POST.get('order_notes', '')

        # Extract district and thana
        district_id, district_name = district_value.split('-', 1) if district_value else ("", "")
        thana_id, thana_name = thana_value.split('-', 1) if thana_value else ("", "")

        # Calculate order costs
        shipping_type = 'flat_rate' if request.POST.get('shipping') == '100' else 'free_shipping'
        shipping_cost = Decimal('100.00') if shipping_type == 'flat_rate' else Decimal('0.00')
        subtotal = sum((item.final_price or 0) * item.quantity for item in cart_items)
        total_amount = subtotal + shipping_cost

        # Step 2: Save CustomerInfo
        customer = CustomerInfo.objects.create(
            CustomerID=f"CUST{phone[-4:]}{CustomerInfo.objects.count()+1}",  # basic auto-id logic
            CustomerName=f"{first_name} {last_name}",
            CustomerAddress=f"{district_name} | {thana_name} | {address} ",
            CustomerEmail=None,
            CustomerContact=phone,
            district_id=district_id,
            district_name=district_name,
            thana_id=thana_id,
            thana_name=thana_name,
            RegDate=date.today(),
            dabite="0",
            cradit="0",
            adminid=None,
            type="general",
            open_due="0"
        )

        # Step 3: Save Order
        order = Order.objects.create(
            customer=customer,
            status=5,
            payment_status='pending',
            order_date=date.today(),
            notes=order_notes,
            subtotal=subtotal,
            shipping_type=shipping_type,
            shipping_cost=shipping_cost,
            total_amount=total_amount
        )

        # Step 4: Save OrderItems
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

        # Step 5: Clear the cart OR buy now session
        if is_buy_now:
            del request.session['buy_now_product']
        else:
            AddCart.objects.all().delete()

        return redirect('thank_you')  # Update with your URL name

    # GET request
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
        'cart_items': cart_items,
        'subtotal': total,
        'total': total + Decimal('100.00'),
        'is_buy_now': is_buy_now,  # Added this line
    }
    return render(request, 'blue_dot/checkout.html', context)



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