
from django.urls import path, include
from . import views

from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.home,name='home'),
    path('category/<slug:slug>/', views.category,name='category'),
    path('productdetail/<slug:slug>/', views.productdetail,name='productdetail'),
    path('shop_view/', views.shop_view,name='shop_view'),
    path('contact_view/', views.contact_view,name='contact_view'),
    
    

   
]
