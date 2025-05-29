from django.shortcuts import render
from backend.models import *
from django.shortcuts import render, redirect
from django.contrib import messages

# Create your views here.



def home(request):
    sliders = HomeSlider.objects.all()  # fetch all sliders
    return render(request, 'blue_dot/index.html', {'sliders': sliders})


def service(request):
    return render(request, 'blue_dot/service.html')

def service_details(request):
    return render(request, 'blue_dot/service-details.html')


def shop(request):
    return render(request, 'blue_dot/shop.html')

def shop_details(request):
    return render(request, 'blue_dot/shop-details.html')

def cart(request):
    return render(request, 'blue_dot/cart.html')

def checkout(request):
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
    
    context = {
        'banner': banner,
        'about': about,
        'cta': cta,
        'choose_us_section': choose_us_section,
        'choose_us_items': choose_us_items,
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
    return render(request, 'blue_dot/faq.html')

def error(request):
    return render(request, 'blue_dot/error.html')