from decimal import Decimal
from os import truncate
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.models import User

from django.middleware.csrf import CsrfViewMiddleware

from django.contrib import messages
from django.db.models import Sum,Q
from django.db.models.functions import TruncDate
from django.utils.timezone import now


from store.models import *
from orders.models import *
from django.contrib.auth import authenticate, logout
from userprofile.models import *

from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.cache import cache_control


def is_superuser(user):
    return user.is_superuser

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='signin')  # This restricts access to superusers only.
def admin_home(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if not start_date and not end_date:
            # Calculate the current date
            current_date = now().date()

            # Calculate the date 30 days back from the current date
            default_start_date = current_date - timedelta(days=30)
            default_end_date = current_date

            # Convert to string format (YYYY-MM-DD)
            start_date = default_start_date.strftime('%Y-%m-%d')
            end_date = default_end_date.strftime('%Y-%m-%d')

        if start_date and end_date:
            # Corrected query filter for start_date and end_date using 'date' lookup
            order_count_date = Order.objects.filter(
                order_date__date__gte=start_date, order_date__date__lte=end_date
            ).exclude(payment_status='CANCELLED').count()

            total_price_date = Order.objects.filter(
                order_date__date__gte=start_date, order_date__date__lte=end_date
            ).exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']

            daily_totals = Order.objects.filter(
                order_date__date__gte=start_date, order_date__date__lte=end_date
            ).exclude(payment_status='CANCELLED').annotate(date=TruncDate('order_date')).values('date').annotate(
                total=Sum('total_price')).order_by('date')

            order_count = Order.objects.exclude(payment_status='CANCELLED').count()
            total_price = Order.objects.exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']
            today = now().date()
            today_orders = Order.objects.filter(order_date__date=today)
            order_count_today = today_orders.count()
            total_price_today = sum(order.total_price for order in today_orders)  # Corrected this line

            recent_orders = Order.objects.order_by('-order_date')[:3]

            # Corrected query for top_selling_products using 'product_id' and 'product__name'
            top_selling_products = OrderItem.objects.values('product__product__name').annotate(
                total_quantity=Sum('quantity')
            ).order_by('-total_quantity')[:5]

            categories = Category.objects.all()
            data = []

            for category in categories:
                product_count = Product.objects.filter(category=category).count()
                data.append(product_count)
            


            context = {
                'order_count_date': order_count_date,
                'total_price_date': total_price_date,
                'start_date': start_date,
                'end_date': end_date,
                'daily_totals': daily_totals,
                'order_count': order_count,
                'total_price': total_price,
                'categories': categories,
                'data': data,
                'order_count_today': order_count_today,
                'total_price_today': total_price_today,
                'recent_orders': recent_orders,
                'top_selling_products': top_selling_products,
            }
            notify = None
            try:
                notify = Notifications.objects.all().exclude(status=False)
                context.update({ 'notify': notify })
            except:
                pass

            return render(request, 'admin_side/home.html', context)

        else:
            order_count = Order.objects.exclude(payment_status='CANCELLED').count()
            total_price = Order.objects.exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']

            today = now().date()
            today_orders = Order.objects.filter(order_date__date=today)
            order_count_today = today_orders.count()
            total_price_today = sum(order.total_price for order in today_orders)  # Corrected this line

            categories = Category.objects.all()
            data = []

            for category in categories:
                product_count = Product.objects.filter(category=category).count()
                data.append(product_count)

            recent_orders = Order.objects.order_by('-order_date')[:3]

            # Corrected query for top_selling_products using 'product_id' and 'product__name'
            top_selling_products = OrderItem.objects.values('product__name').annotate(
                total_quantity=Sum('quantity')
            ).order_by('-total_quantity')[:5]

            context = {
                'order_count': order_count,
                'total_price': total_price,
                'start_date': start_date,
                'end_date': end_date,
                'order_count_today': order_count_today,
                'total_price_today': total_price_today,
                'categories': categories,
                'data': data,
                'recent_orders': recent_orders,
                'top_selling_products': top_selling_products,
            }

            return render(request, 'admin_side/home.html', context)

    return HttpResponseBadRequest("Invalid requestmethod.")


def log_out(request):
    if request.user.is_superuser:
        logout(request)
        messages.success(request, 'Admin You Logged out successfully')
        return redirect('home')

def users(request):
    user = User.objects.all().order_by('id')
    context = {
        'user':user
    }
    return render(request, 'admin_side/user_list.html', context)



def block_user(request,user_id):
    user = User.objects.get(id=user_id)
    user.is_active=False
    user.save()
    return redirect('userslist')

def unblock_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active=True
    user.save()
    return redirect('userslist')

def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect('userslist')


def productlist(request):
    products = Product.objects.all().order_by()

    
    return render(request, 'admin_side/product_list.html', {'products':products})



def enable_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.is_active=True
    product.save()
    return redirect('productlist')

def disable_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.is_active=False
    product.save()
    return redirect('productlist')

def product_list_view(request, product_id):
    if request.user.is_superuser:
        print('ethiyo======>')

        product = get_object_or_404(Product, id=product_id)

        variants = product.productvariant_set.all()

        context = {
            'product': product,
            'variants': variants
        }
        return render(request, 'admin_side/admin_variants.html', context)


def add_varients(request, id):
    if request.user.is_superuser:
        if request.method == 'POST':
            model_name = request.POST['model_name']
            color = request.POST['color']
            store_price = request.POST['store_price']
            sale_price = request.POST['sale_price']
            discount = request.POST['Discount']
            stock = request.POST['stock']
            product = get_object_or_404(Product, id=id)
            colour = get_object_or_404(Color, id=color)
            
            if discount:
                discount = float(discount)
                discount_price= float(sale_price) - (float(sale_price)*discount/100)
            else:
                discount_price=None

            # Check if a variant with the same color already exists for the product
            existing_variant = ProductVariant.objects.filter(product=product, color=colour).first()
            if existing_variant:
                # Variant with the same color already exists, show an error message
                error_message = f"A variant with the color '{colour}' already exists for this product."
                colours = Color.objects.all()
                return render(request, 'admin_side/add_variant.html', {'colours': colours, 'error_message': error_message})

            new_variant = ProductVariant.objects.create(
                product=product,
                model_name=model_name,
                color=colour,
                store_price=store_price,
                sale_price=sale_price,
                discount=discount,
                discount_price=discount_price,
                stock=stock
            )

            variant_images = request.FILES.getlist('images')
            for img in variant_images:
                ProductImage.objects.create(variant=new_variant, image=img)

            return redirect('productlist')

        colours = Color.objects.all()
        
        return render(request, 'admin_side/add_variant.html', {'colours': colours})
    else:
        return render(request,'home.html')


def edit_variant(request, variant_id):
    product_variant = ProductVariant.objects.get(id=variant_id)
    print('variant====>', product_variant)

    if request.method == "POST":
        product_variant.model_name = request.POST['model_name']
        color_id = request.POST.get('color')
        product_variant.color = get_object_or_404(Color, pk=color_id)
        product_variant.store_price = request.POST['store_price'] or 0.00
        product_variant.sale_price = request.POST['sale_price']
        product_variant.discount_percentage = request.POST['discount_percentage']

        stock_change = int(request.POST['stock'])  # Convert to integer

        if product_variant.stock:
            product_variant.stock += stock_change
        else:
            product_variant.stock = stock_change

        variant_image = request.FILES.getlist('images')
        if variant_image:
            existing_images = ProductImage.objects.filter(variant=product_variant)
            existing_images.delete()

            for img in variant_image:
                ProductImage.objects.create(variant=product_variant, image=img)

        product_variant.save()

        return redirect('productlist')
    
    colors = Color.objects.all()
    variants = ProductVariant.objects.all()
    images = ProductImage.objects.filter(variant=product_variant)
    
    context = {
        'colors': colors,
        'variants': variants,
        'images': images,
        'product_variant': product_variant
    }

    return render(request, 'admin_side/edit_variant.html', context)

   


from django.http import HttpResponse

def add_products(request):
    if request.method == 'POST':
        Name = request.POST['name']
        description = request.POST['shortdescription']
        created = request.POST['created_at']
        updated = request.POST['updated_at']

        category = request.POST['category']
        cat_id = get_object_or_404(Category, id=category)

        brand = request.POST['brands']
        brand_id = get_object_or_404(Brands, id=brand)

        # Check if the product with the same name already exists
        existing_product = Product.objects.filter(name=Name).first()
        if existing_product:
            error_message = f"A product with the name '{Name}' already exists."

            categories = Category.objects.all()
            color = Color.objects.all()
            brands = Brands.objects.all()
            
            context = {
                'categories':categories,
                'color':color,
                'brands':brands,
                'error_message': error_message
            } 

            return render(request, 'admin_side/admin_add_products.html', context)

        prod = Product.objects.create(
            name=Name,
            description=description,
            created_at=created,
            updated_at=updated,
            category=cat_id,
            brand_name=brand_id)

        # variants add
        colors = request.POST['color']
        colour = get_object_or_404(Color, id=colors)

        product = get_object_or_404(Product, id=prod.id)

        prices = request.POST['prices']
        store_price = request.POST['store_prices']
        stockes = request.POST['stockes']


        new_variant = ProductVariant.objects.create(
            product=product,
            color=colour,
            sale_price=prices,
            store_price=store_price,
            stock=stockes
        )

        # add product variant images
        variant_images = request.FILES.getlist('images')

        for img in variant_images:
            new = ProductImage.objects.create(variant=new_variant, image=img)

        return redirect('productlist')



    categories = Category.objects.all()
    color = Color.objects.all()
    brands = Brands.objects.all()

    contex = {
                'categories':categories,
                'color':color,
                'brands':brands
    } 
    return render(request, 'admin_side/admin_add_products.html', contex)



def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        product.name = request.POST['name']
        product.description = request.POST['description']
        category_id = request.POST.get('categorySelect')
        product.category = get_object_or_404(Category, id=category_id)
        # gender_id = request.POST.get('genderSelect')
        # product.gender = get_object_or_404(Gender, pk=gender_id)

        brand_id = request.POST.get('brand_name')
        print('=====>',brand_id)
        product.brand_name = get_object_or_404(Brands, pk=brand_id)


      

        
        product.save()

        return redirect('productlist')
    
    categories = Category.objects.all()
    # gender = Gender.objects.all()
    brand_name = Brands.objects.all()
    

    contex={
        'categories':categories,
        # 'gender':gender,
        'brand_name':brand_name,
        'product':product
    }
    
    return render(request, 'admin_side/edit_product.html', contex)
        


def category_list(request):
    categories = Category.objects.all().order_by('id')
    contex ={
        'categories':categories
    }
    return render(request, 'admin_side/category_list.html', contex)





def add_category(request):

    if request.method == 'POST':
        category_name = request.POST['name']
        category_image = request.FILES.get('image') 

        new_category = Category.objects.create(name=category_name, image=category_image)
        new_category.save()
        

        return redirect('category_list')

    return render(request, 'admin_side/add_category.html')




def edit_category(request, category_id):
    
    category = Category.objects.get(id=category_id)
    

    if request.method == 'POST':

        category.name = request.POST['category_name']

        
        image = request.FILES.get('images')
        if image : 
            category.image=image
        category.save()

        return redirect('category_list')
    
    contex={
       'category': category,
       
    }
    
    return render(request, 'admin_side/edit_category.html', contex)







def disable_category(request, variant_id):

    if request.user.is_superuser:

        category = get_object_or_404(Category, id=variant_id)
        category.is_active = False
        category.save()

        return redirect('category_list')
    
def enable_category(request, variant_id):
    if request.user.is_superuser:

        category = get_object_or_404(Category, id=variant_id)
        category.is_active = True
        category.save()

        return redirect('category_list')

def admin_orders_list(request):
    if request.user.is_superuser:
        orders = Order.objects.order_by('-id')
        return render(request, 'admin_side/allorder.html', {'orders':orders})
    else:
        return redirect("home")
    

def admin_order_view(request, order_id):
    if request.user.is_superuser:
        view_order = get_object_or_404(Order, id=order_id)
        order = OrderItem.objects.filter(order=view_order)

        context ={
            'order':order,
            'view_order':view_order
        }

    return render(request, 'admin_side/admin_order_view.html', context)



def admin_brand_list(request):
    brands = Brands.objects.all().order_by('id')
    contex ={
        'brands':brands
    }
    return render(request, 'admin_side/brand_list.html', contex)

def order_shipped(request, order_id):
    if request.user.is_superuser:
        
        order = get_object_or_404(Order, id=order_id)
        
        order.order_status = 'Shipped'
        print(order.order_status)
        order.shipping_date = timezone.now()
        order.save()
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return render(request, 'home.html')
    
    
def admin_order_cancel(request, order_id):
    
    if request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)
        user = order.user
        if order.order_status != 'Delivered' and order.order_status != 'Returned' and order.order_status != 'Cancelled' and order.order_status != 'Requested for return':
            
            
            if order.payment_method in ['WALLET']:
                
                user_wallet = Wallet.objects.get(user=user)
                refund_amount = order.total_price
                user_wallet.balance += Decimal(refund_amount)
                user_wallet.save()

                transaction_type = 'Cancelled'
                WalletTransaction.objects.create(wallet=user_wallet, amount=refund_amount, order_id=order, transaction_type=transaction_type)

                if order.payment_status == 'Pending':
                    order.payment_status = 'No payment'
                else:
                    order.payment_status = 'Refunded'
                order.order_status = 'Cancelled'
                Order.cancelled_date = timezone.now()
                order.save()
                try:
                    notify = Notifications.objects.get(order=order)
                    notify.status = False
                    notify.save()
                except:
                    pass

                return redirect(request.META.get('HTTP_REFERER'))

            if order.payment_method in ['RAZORPAY']:
                
                user_wallet = Wallet.objects.get(user=user)
                refund_amount = order.total_price

                user_wallet.balance += Decimal(refund_amount)
                user_wallet.save()
                transaction_type = 'Cancelled'
                WalletTransaction.objects.create(wallet=user_wallet, amount=refund_amount, order_id=order, transaction_type=transaction_type)

                if order.payment_status == 'Pending':
                    order.payment_status = 'No payment'
                else:
                    order.payment_status = 'Refunded'
                    order.order_status = 'Cancelled'
                Order.cancelled_date = timezone.now()
                order.save()
                try:
                    notify = Notifications.objects.get(order=order)
                    notify.status = False
                    notify.save()
                except:
                    pass

                return redirect(request.META.get('HTTP_REFERER'))
    else:
        return render(request, 'home.html')

    
    
def order_deliverd(request, order_id):
    if request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)
        print(order)
        # Make sure the order is in the 'SHIPPED' status before marking it as 'DELIVERED'
        if order.order_status == 'Shipped':
            order.order_status = 'Delivered'
            order.delivery_date=timezone.now()
            order.return_period_expired=timezone.now()+timezone.timedelta(days=5)

        if order.payment_status=='Pending':
            order.payment_status='Paid'
        order.save()
        print(order.return_period_expired)

        return redirect(request.META.get('HTTP_REFERER'))


def admin_brand_edit(request, brand_id):
    
    brand = Brands.objects.get(id=brand_id)
    

    if request.method == 'POST':

        brand.name = request.POST['brand_name']

        brand.save()

        return redirect('admin_brand_list')
    
    contex={
       'brand': brand,
       
    }
    
    return render(request, 'admin_side/edit_brand.html', contex)


def add_brand(request):

    if request.method == 'POST':
        brand_name = request.POST['name']
        brand=Brands(name=brand_name)
        
        brand.save()

        return redirect('admin_brand_list')

    return render(request, 'admin_side/add_brand.html')


from django.db.models import Q, Sum
from datetime import timedelta
from django.utils import timezone


def sales_view(request):
    today = timezone.now().date()
    
    
    week_ago = today - timedelta(days=7)

    month_ago = today - timedelta(days=30)


    today_orders = Order.objects.filter(order_date__date=today)
    


    order_count_today = today_orders.count()

    total_price_today = today_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0


    week_orders = Order.objects.filter(order_date__range=[week_ago, today], ).exclude(Q(order_status='Returned') | Q(order_status='Cancelled'))
    
    order_count_week = week_orders.count()

    total_price_week = week_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
 

    month_orders = Order.objects.filter(order_date__range=[month_ago, today] ).exclude(Q(order_status='Returned') | Q(order_status='Cancelled'))
    order_count_month = month_orders.count()
    total_price_month = month_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0

    top_selling_variants_today = OrderItem.objects.filter(order__in=today_orders).values(
        'product__product__name', 'product__color__color').annotate(total_quantity=Sum('quantity')).order_by(
        '-total_quantity')[:5]

    top_selling_variants_week = OrderItem.objects.filter(order__in=week_orders).values(
        'product__product__name', 'product__color__color').annotate(total_quantity=Sum('quantity')).order_by(
        '-total_quantity')[:5]  

    top_selling_variants_month = OrderItem.objects.filter(order__in=month_orders).values(
        'product__product__name', 'product__color__color').annotate(total_quantity=Sum('quantity')).order_by(
        '-total_quantity')[:5]



    
    context = {
        'order_count_today': order_count_today,
        'total_price_today': total_price_today,
        'order_count_week': order_count_week,
        'total_price_week': total_price_week,
        'order_count_month': order_count_month,
        'total_price_month': total_price_month,
        'top_selling_variants_today': top_selling_variants_today,
        'top_selling_variants_week': top_selling_variants_week,
        'top_selling_variants_month': top_selling_variants_month,
    }

    return render(request, 'admin_side/sales_report.html', context)

from django.template.loader import render_to_string
from xhtml2pdf import pisa

def generate_pdf(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    today_orders = Order.objects.filter(order_date__date=today,).exclude(Q(order_status='Returned') | Q(order_status='Cancelled'))

    order_count_today = today_orders.count()
    total_price_today = today_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0

    week_orders = Order.objects.filter(order_date__range=[week_ago, today], ).exclude(Q(order_status='Returned') | Q(order_status='Cancelled'))
    
    order_count_week = week_orders.count()
    total_price_week = week_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
 

    month_orders = Order.objects.filter(order_date__range=[month_ago, today] ).exclude(Q(order_status='Returned') | Q(order_status='Cancelled'))

    order_count_month = month_orders.count()
    total_price_month = month_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0

    top_selling_variants_today = OrderItem.objects.filter(order__in=today_orders).values(
        'product__product__name', 'product__color__color').annotate(total_quantity=Sum('quantity')).order_by(
        '-total_quantity')[:5]

    top_selling_variants_week = OrderItem.objects.filter(order__in=week_orders).values(
        'product__product__name', 'product__color__color').annotate(total_quantity=Sum('quantity')).order_by(
        '-total_quantity')[:5]  

    top_selling_variants_month = OrderItem.objects.filter(order__in=month_orders).values(
        'product__product__name', 'product__color__color').annotate(total_quantity=Sum('quantity')).order_by(
        '-total_quantity')[:5]
    context = {
        'today_orders':today_orders,
        'order_count_today':order_count_today,
        'total_price_today':total_price_today,
        'week_orders':week_orders,
        'order_count_week':order_count_week,
        'total_price_week':total_price_week,
        'month_orders':month_orders,
        'order_count_month':order_count_month,
        'total_price_month':total_price_month,
        'top_selling_variants_today':top_selling_variants_today,
        'top_selling_variants_week':top_selling_variants_week,
        'top_selling_variants_month':top_selling_variants_month

    }

    template = 'sales_report_pdf.html'
    html_string = render_to_string(template, context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="sales_report.pdf"'

    pisa_status = pisa.CreatePDF(html_string, dest=response )
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
    return response

