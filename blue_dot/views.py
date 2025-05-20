from django.shortcuts import render

# Create your views here.



def home(request):
    
    return render(request, 'blue_dot/index.html')


def service(request):
    return render(request, 'blue_dot/service.html')

def service_details(request):
    return render(request, 'blue_dot/service-details.html')