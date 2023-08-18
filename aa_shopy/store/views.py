from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render 
from .models import *
from store.models import *


# Create your views here.
def home(request):
    categories = Category.objects.filter(is_active=True)
    banners = BannerImage.objects.all()
    products = Product.objects.filter(is_active=True)

    
    paginator = Paginator(products, 6) 

    page_number = request.GET.get('page')
    products_paginator = paginator.get_page(page_number)

    
    

    return render(request, 'home.html', {'categories': categories, 'products': products_paginator , 'banners' : banners})

    
 
def category(request, slug):
    
    current_categories = get_object_or_404(Category, slug=slug)
    products = current_categories.product_set.all()  # Retrieve products based on the category
    categories = Category.objects.all()

    print("Retrieve products based on the category------>", products)  # Check the products in the console
    return render(request, 'category.html', {'products': products, 'categories': categories})




def productdetail(request, slug):
    
    product_variant = get_object_or_404(ProductVariant, slug=slug)
    product = product_variant.product
    images = ProductImage.objects.filter(variant=product_variant)
    categories = Category.objects.all()
    if request.method == 'POST':
        # Get the selected variant ID from the submitted form data
        variant_id = request.POST.get('variant_id', None)
        if variant_id:
            selected_variant = get_object_or_404(ProductVariant, id=variant_id)
            # Update the product details to show the selected variant
            product = selected_variant.product
            images = ProductImage.objects.filter(variant=selected_variant)
            return render(request, 'product_details.html', {
                'product': product,
                'product_variant': selected_variant,
                'images': images,
                'selected_variant': selected_variant
            })

    return render(request, 'product_details.html', {
        'product': product,
        'product_variant': product_variant,
        'images': images,
        'selected_variant': product_variant,
        'categories':categories
    })


from django.core.paginator import Paginator
def shop_view(request):

    products = Product.objects.filter(is_active=True)
    price = ProductVariant.objects.filter(product__in=products).all()
    categories = Category.objects.all()
    brands = Brands.objects.all()  

    if request.method == 'POST':
        search_items = request.POST['text']
        if search_items:
            # Perform the search query using the 'contains' lookup on the product name or description
            products = Product.objects.filter(name__icontains=search_items) | Product.objects.filter(description__icontains=search_items)
        
    if request.method == "GET":
        # Handling filters from the request
        category_filter = request.GET.get('categoryFilter')
        brand_filter = request.GET.get('brandFilter')
        price_filter = request.GET.get('priceFilter')

        # Apply the filters to the products queryset based on the criteria
        if category_filter and category_filter != 'all':
            products = products.filter(category=category_filter)

        if brand_filter and brand_filter != 'all':
            products = products.filter(brand_name=brand_filter)

         # Apply other filters based on the 'price_filter' value as needed
        if price_filter == 'under50':
            products = products.filter(productvariant__sale_price__lt=5000)
        elif price_filter == '50to100':
            products = products.filter(productvariant__sale_price__range=(5000, 30000))
        elif price_filter == '100to200':
            products = products.filter(productvariant__sale_price__range=(30000, 50000))
        #Add more price range options as needed

    
    paginator = Paginator(products, 6) 

    page_number = request.GET.get('page')
    products_paginator = paginator.get_page(page_number)


    context = {
        "products": products_paginator,
        "price": price,  # Add price to the context for the template
        'categories': categories,
        'brands': brands,
        
    }

    return render(request, 'shop.html', context)


def contact_view(request):
    return render(request, 'contact.html')