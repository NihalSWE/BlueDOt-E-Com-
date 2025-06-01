from django.urls import path
from . import views
# from . import views_admin
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.deshboard, name='dashboard'),
    
    # home page
    # path('home',views.home,name='admin-home'),
    path('home/banner/',views.home_banner,name='home_banner'),
    path('home/practice-area/',views.practice_area,name='practice_area'),
    path('home/practice-area-create/',views.practice_area_create, name='practice_area_create'),
    path('home_centerCard',views.home_centerCard,name='home_centerCard'),
    path('home-center-card/edit/<int:card_id>/', views.edit_center_card, name='edit_center_card'),
    path('home-center-card/delete/<int:card_id>/', views.delete_center_card, name='delete_center_card'),
    # path('home_CTA',views.home_CTA,name='home_CTA'),
    
    path('contactUs',views.contactUs,name='contactUs'),
    path('contactUs_location',views.contactUs_location,name='contactUs_location'),
    path('contactUs_msg',views.contactUs_msg,name='contactUs_msg'),
    
    path('aboutUs_banner',views.aboutUs_banner,name='aboutUs_banner'),
    path('aboutUs_aboutarea',views.aboutUs_aboutarea,name='aboutUs_aboutarea'),
    path('aboutUs_callToaction',views.aboutUs_callToaction,name='aboutUs_callToaction'),
    path('aboutUs_chooseUs',views.aboutUs_chooseUs,name='aboutUs_chooseUs'),
    path('aboutus_faq',views.aboutus_faq,name='aboutus_faq'),
    
    path('Ourfaq_banner',views.Ourfaq_banner,name='Ourfaq_banner'),
    path('Ourfaq_faqs',views.Ourfaq_faqs,name='Ourfaq_faqs'),
    
    path('product_list/',views.product_list,name='product_list'),
    path('add_product/',views.add_product,name='add_product'),
    path('category_list',views.category_list,name='category_list'),
    path('order_list',views.order_list,name='order_list'),
    path('order_detail',views.order_detail,name='order_detail'),
    path('customer_list',views.customer_list,name='customer_list'),
    path('customer_overview',views.customer_overview,name='customer_overview'),
    path('security',views.security,name='security'),
    path('billing',views.billing,name='billing'),
    path('notification',views.notification,name='notification'),
    path('store_details',views.store_details,name='store_details'),
    path('payments',views.payments,name='payments'),
    path('checkout',views.checkout,name='checkout'),
    path('shipping',views.shipping,name='shipping'),
    path('location',views.location,name='location'),
    path('setting_notification',views.setting_notification,name='setting_notification'),
    path('invoice_add',views.invoice_add,name='invoice_add'),
    path('invoice_edit',views.invoice_edit,name='invoice_edit'),
    path('invoice_preview',views.invoice_preview,name='invoice_preview'),
    path('invoice_list',views.invoice_list,name='invoice_list'),
    path('access_roles',views.access_roles,name='access_roles'),
    path('access_permission',views.access_permission,name='access_permission'),
    
]