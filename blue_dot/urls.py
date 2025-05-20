from django.urls import path
from . import views
# from . import views_admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('service/',views.service,name='service'),
    path('service_details/',views.service_details,name='service_details'),
]


