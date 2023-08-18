from django.urls import path
from . import views

urlpatterns = [
    path('adminhome/', views.admin_home, name='adminhome'),
    path('users/', views.users, name='userslist'),
    path('block/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('productlist/', views.productlist, name='productlist'),
    path('enable_product/<int:product_id>/', views.enable_product, name='enable_product'),
    path('disable_product/<int:product_id>/', views.disable_product, name='disable_product'),
    path('log_out/', views.log_out, name='log_out'),
    
    path('product_list_view/<int:product_id>/', views.product_list_view, name='product_list_view'),
    path('add_varients/<int:id>/',views.add_varients,name='add_varients'),
    path('edit_variant/<int:variant_id>/',views.edit_variant,name='edit_variant'),

    path('add_products/', views.add_products,name='add_products'),
    path('edit_product/<int:product_id>', views.edit_product,name='edit_product'),
    

    path('category_list/', views.category_list,name='category_list'), 
    path('edit_category/<int:category_id>', views.edit_category,name='edit_category'), 

    path('add_category/', views.add_category,name='add_category'), 

    path('disable_category/<int:variant_id>/', views.disable_category,name='disable_category'), 
    path('enable_category/<int:variant_id>/', views.enable_category,name='enable_category'), 

    path('admin_orders_list/', views.admin_orders_list,name='admin_orders_list'), 
    path('admin_order_view/<int:order_id>', views.admin_order_view,name='admin_order_view'), 

    path('admin_brand_list/', views.admin_brand_list, name='admin_brand_list'),
    path('admin-brand-edit/<int:brand_id>', views.admin_brand_edit, name='admin_brand_edit'),
    path('admin-brand-add/', views.add_brand, name='add_brand'),

    path('order_shipped/<int:order_id>', views.order_shipped,name='order_shipped'), 
    path('admin_order_cancel/<int:order_id>', views.admin_order_cancel,name='admin_order_cancel'), 
    path('order_deliverd/<int:order_id>', views.order_deliverd,name='order_deliverd'), 

    path('sales_view/', views.sales_view, name='sales_view'),
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),
    
    


]