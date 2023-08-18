from django.urls import path, include
from . import views

urlpatterns = [
    path('checkout_page',views.checkout_page,name='checkout_page'),

    path('initiate_payment/', views.initiate_payment, name='initiate_payment'),
    path('online_payment_order/<userId>',views.online_payment_order,name='online_payment_order'),
    path('order_success',views.order_success,name='order_success'),
    
    path('place_order/<int:selected_address_id>',views.place_order,name='place_order'),
    path('wallet_place_order/<int:selected_address_id>',views.wallet_place_order,name='wallet_place_order'),
    path('orders_list/',views.orders_list,name='orders_list'),
    path('order_detail/<int:order_id>',views.order_detail,name='order_detail'),

    path('order_cancel/<int:order_id>/', views.order_cancel, name='order_cancel'),

]
