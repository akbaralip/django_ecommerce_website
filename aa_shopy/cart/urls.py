from django.urls import path, include
from . import views

urlpatterns = [
    path('add_to_cart/<int:selected_variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('remove_coupon/', views.remove_coupon, name='remove_coupon'),


    path('wishlist/', views.wishlist, name='wishlist'),
    path('remove_to_wishlist/<int:item_id>', views.remove_to_wishlist, name='remove_to_wishlist'),

    
    
    path('update_quantity/', views.update_quantity, name='update_quantity'),
    path('add_to_wishlist/<int:selected_variant_id>/', views.add_to_wishlist, name='add_to_wishlist'),

    path('create_coupon/', views.create_coupon, name="create_coupon"),
    path('add_coupon/', views.add_coupon, name="add_coupon"),
    path('coupon_list/', views.coupon_list, name="coupon_list"),
    

    


]
