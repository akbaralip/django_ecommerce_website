from django.urls import path
from . import views
urlpatterns = [
    path('user_profile/', views.user_profile, name='user_profile'),

    path('address_view/', views.address_view, name='address_view'),
    path('add_address/', views.add_address, name='add_address'),
    path('edit_address/<int:address_id>', views.edit_address, name='edit_address'),
    path('delete_address/<int:address_id>', views.delete_address, name='delete_address'),
    path('choose_delivery_address/<int:address_id>', views.choose_delivery_address, name='choose_delivery_address'),

    path('password_reset/', views.password_reset, name='password_reset'),

    path('user_view_wallet/', views.user_view_wallet, name='user_view_wallet'),
    


]
