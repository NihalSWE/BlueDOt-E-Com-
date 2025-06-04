from django.shortcuts import render
from backend.models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from backend.models import *
from django.shortcuts import render, get_object_or_404
from backend.forms import *
# Create your views here.



def home(request):
    sliders = HomeSlider.objects.all()
    center_cards = CenterCard.objects.all()  # Add this line
    products = Product.objects.order_by('-created_at')[:8]
    home_cta = HomeCTA.objects.first()  # Get the CTA (assuming one exists)
    pricing_card = PricingCard.objects.first()  # Fetch the PricingCard content
    category_products = Product.objects.order_by('-created_at')[:4]
    return render(request, 'blue_dot/index.html', {
        'sliders': sliders,
        'center_cards': center_cards,
        'products': products,
        'home_cta':home_cta,
        'pricing_card':pricing_card,
        'category_products':category_products
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


def cart(request):
    return render(request, 'blue_dot/cart.html')

def checkout(request):
    return render(request, 'blue_dot/checkout.html')

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




