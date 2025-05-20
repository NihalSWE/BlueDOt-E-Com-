from django.urls import path
from . import views
# from . import views_admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('service/',views.service,name='service'),
    path('service_details/',views.service_details,name='service_details'),
    path('shop/',views.shop,name='shop'),
    path('shop_details/',views.shop_details,name='shop_details'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('blog/',views.blog,name='blog'),
    path('blog_details/',views.blog_details,name='blog_details'),
    path('blog_sidebar/',views.blog_sidebar,name='blog_sidebar'),
    path('contact/',views.contact,name='contact'),
    path('aboutUs/',views.aboutUs,name="aboutUs"),
    path('ourteam/',views.ourteam,name='ourteam'),
    
     
    
]


