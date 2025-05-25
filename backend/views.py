from django.shortcuts import render

# Create your views here.


def deshboard(request):
    return render(request, 'backend/index.html')

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