from django.shortcuts import render

# Create your views here.



def home(request):
    
    return render(request, 'blue_dot/index.html')


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
    return render(request, 'blue_dot/contact.html')

def aboutUs(request):
    return render(request, 'blue_dot/about.html')

def ourteam(request):
    return render(request, 'blue_dot/team.html')