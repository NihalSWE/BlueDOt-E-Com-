from django.shortcuts import render
from backend.models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from backend.models import *
from backend.forms import *
from django.shortcuts import render, get_object_or_404


# Create your views here.



def home(request):
    sliders = HomeSlider.objects.all()
    center_cards = CenterCard.objects.all()  # Add this line
    products = Product.objects.order_by('-created_at')[:8]
    home_cta = HomeCTA.objects.first()  # Get the CTA (assuming one exists)
    pricing_card = PricingCard.objects.first()  # Fetch the PricingCard content
    category_products = Product.objects.order_by('-created_at')[:4]
    blogs = BlogPost.objects.filter(is_active=True)
    return render(request, 'blue_dot/index.html', {
        'sliders': sliders,
        'center_cards': center_cards,
        'products': products,
        'home_cta':home_cta,
        'pricing_card':pricing_card,
        'category_products':category_products,
        'blogs':blogs
    })
    

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




def cart_checkout(request):
    return render(request, 'blue_dot/checkout.html')

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
    categories = DiscountCategory.objects.filter(
        status=1,
        start_date__lte=now,
        end_date__gte=now
    ).order_by('name')
    return render(request, 'blue_dot/discount.html', {
        'categories': categories,
        'current_date': now
    })

def category_products(request, slug):
    category = get_object_or_404(DiscountCategory, slug=slug, status=1)
    discounts = category.discounts.filter(status=1)

    product_ids = discounts.values_list('products__id', flat=True).distinct()

    products = Product.objects.filter(id__in=product_ids).select_related('category', 'brand')

    # Calculate discount percentage for each product
    for product in products:
        # Find applicable discount for this product from discounts queryset
        # Assuming discounts have product relation and discount price or percent
        applicable_discount = discounts.filter(products=product).first()
        if applicable_discount:
            base_price = product.base_price
            final_price = product.final_price
            if base_price > 0 and final_price < base_price:
                discount = ((base_price - final_price) / base_price) * 100
                product.discount_percent = int(round(discount))
            else:
                product.discount_percent = 0
        else:
            product.discount_percent = 0

    return render(request, 'blue_dot/discount_category_products.html', {
        'category': category,
        'products': products,
        'discounts': discounts,
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




def shop(request):
    banner=ProductBanner.objects.last()
    categories = Category.objects.all()
    products = Product.objects.all()
    recent_products = Product.objects.order_by('-created_at')[:3]
    print('categories: ', categories)
    context = {
        'categories': categories,
        'products': products,
        'recent_products': recent_products,
        'banner':banner
    }
    return render(request, 'blue_dot/shop.html', context)



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


from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def cart(request):
    banner = CartBanner.objects.first()
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



