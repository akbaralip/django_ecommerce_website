from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import  HttpResponseRedirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from .models import Coupon
from django.core.exceptions import ObjectDoesNotExist

from decimal import Decimal

def add_to_cart(request, selected_variant_id):
    product_variant = ProductVariant.objects.get(id=selected_variant_id)
    user = request.user

    if user.is_authenticated:
        # Retrieve the current user's cart or create a new one if it doesn't exist
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart.objects.create(user=None)  # Set the user field to None for guest users
            request.session['cart_id'] = cart.id

    item = cart.cartitems_set.filter(product=product_variant).first()

    if item:
        available_stock = product_variant.stock - item.quantity
        request_quantity = 1

        if available_stock >= request_quantity:
            item.quantity += request_quantity
            item.save()
            messages.success(request, 'Item added to cart.')
        else:
            messages.error(request, 'Requested quantity exceeds available stock')
    else:
        if product_variant.stock >= 1:
            # Check if the product has a discount_price and use that, otherwise use sale_price
            item_price = product_variant.discount_price if product_variant.discount_price else product_variant.sale_price
            print(item_price)
            CartItems.objects.create(cart=cart, product=product_variant, quantity=1, price=item_price)
            messages.success(request, 'Item added to cart.')
        else:
            messages.error(request, 'Requested quantity exceeds available stock')

    return HttpResponseRedirect(request.META['HTTP_REFERER'])

 
def cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        print('guest_cart:', cart_id)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart.objects.create(user=None)
            request.session['cart_id'] = cart.id

    cart_items = cart.cartitems_set.all()
    # total = cart.get_total_price()
    total = cart.get_total_price() or 0
   


    

    # Check if cart items count is 0 and reset coupon
    if cart_items.count() == 0:
        cart.coupon = None 
        cart.save()

    if request.method == 'POST':
        coupon_code = request.POST.get('coupon')

        try:
            coupon = Coupon.objects.get(code=coupon_code)

            if coupon.valid_to and total >= coupon.minimum_order_amount:
                usercoupon = Usercoupon.objects.filter(coupon=coupon, user=request.user)
                
                if not usercoupon.exists():
                    cart.coupon = coupon
                    cart.save()
                    
                    # # Create a Usercoupon instance to record that the user applied this coupon
                    # Usercoupon.objects.create(user=request.user, coupon=coupon, total_price=total)
                    messages.success(request, 'Coupon applied successfully.')
                else:
                    messages.error(request, 'Coupon already applied')
            else:
                messages.error(request, 'Invalid coupon.')

            return redirect('cart')

        except ObjectDoesNotExist:
            messages.error(request, 'Coupon does not exist.')
            return redirect('cart')

    discount_coupon = cart.coupon.discount if cart.coupon else 0

    total_price = sub_total = total_discount = coupon_applied_total = 0

    for item in cart_items:
        item_price = item.product.discount_price if item.product.discount_price else item.product.sale_price
        item_total = item_price * item.quantity
        total_price += item_total
        

        if item.product.discount_price:
            
            total_discount += (item.product.sale_price - item.product.discount_price) * item.quantity
            
        sub_total += item.product.sale_price * item.quantity

    request.session['total_discount']=str(total_discount)
    

    change_amount =total_price - discount_coupon
    
   
    context = {
        'cart_items': cart_items,
        'cart': cart,
        'total_price': total_price,
        'total_discount': total_discount,
        'change_amount': change_amount,
        'sub_total': sub_total,
        'discount_coupon': discount_coupon,
        
    }

    return render(request, 'cart/cart.html', context)

# def cart(request):
#     if request.user.is_authenticated:
#         cart, created = Cart.objects.get_or_create(user=request.user)
#     else:
#         cart_id = request.session.get('cart_id')
#         if cart_id:
#             cart = Cart.objects.get(id=cart_id)
#         else:
#             cart = Cart.objects.create(user=None)
#             request.session['cart_id'] = cart.id

#     cart_items = cart.cartitems_set.all()
#     total = cart.get_total_price() or 0

#     if cart_items.count() == 0:
#         cart.coupon = None 
#         cart.save()

#     if request.method == 'POST':
#         coupon_code = request.POST.get('coupon')

#         try:
#             coupon = Coupon.objects.get(code=coupon_code)

#             if coupon.valid_to and total >= coupon.minimum_order_amount:
#                 usercoupon = Usercoupon.objects.filter(coupon=coupon, user=request.user)
                
#                 if not usercoupon.exists():
#                     cart.coupon = coupon
#                     cart.save()
#                     messages.success(request, 'Coupon applied successfully.')
#                 else:
#                     messages.error(request, 'Coupon already applied')
#             else:
#                 messages.error(request, 'Invalid coupon.')

#             return redirect('cart')

#         except ObjectDoesNotExist:
#             messages.error(request, 'Coupon does not exist.')
#             return redirect('cart')

#     discount_coupon = cart.coupon.discount if cart.coupon else 0

#     total_price = sub_total = total_discount = coupon_applied_total = 0

#     for item in cart_items:
#         item_price = item.product.discount_price if item.product.discount_price else item.product.sale_price
#         item_total = item_price * item.quantity
#         total_price += item_total

#         if item.product.discount_price:
#             total_discount += (item.product.sale_price - item.product.discount_price) * item.quantity
            
#         sub_total += item.product.sale_price * item.quantity

#     request.session['total_discount'] = str(total_discount)

#     change_amount = total - total_discount - discount_coupon

#     context = {
#         'cart_items': cart_items,
#         'cart': cart,
#         'total_price': total_price,
#         'total_discount': total_discount,
#         'change_amount': change_amount,
#         'sub_total': sub_total,
#         'discount_coupon': discount_coupon
#     }

#     return render(request, 'cart/cart.html', context)

def remove_coupon(request):
    
    carts = Cart.objects.get(user=request.user)
    carts.coupon = None
    carts.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
   


def remove_from_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        print(item_id)

        cart_item = CartItems.objects.filter(id=item_id).first()

        if cart_item:
            cart_item.delete()

        return redirect('cart')
    
    return render(request, 'cart/cart.html')


@login_required
def wishlist(request):

    wishlist, created = WishList.objects.get_or_create(user=request.user)
    
    user_product = CartItems.objects.filter(cart__user=request.user).values_list('product__id', flat=True)
    
    categories = Category.objects.all()
    items = WishListItem.objects.filter(wishlist=wishlist)
    print('items:',items)
    

    context = {
        'wishlist': wishlist,
        'items': items,
        'user_product': user_product ,
        'categories':categories
    }
    if not items:
        return render(request, "cart/no_cart_items.html", context)
    else:
        return render(request, "cart/view_wishlist.html", context)


def add_to_wishlist(request, selected_variant_id):

    if request.user.is_authenticated:
        variant = ProductVariant.objects.get(id=selected_variant_id)
        # Get or create the user's wishlist
        created, wish = WishList.objects.get_or_create(user=request.user)  # Unpack the tuple
        # Check if the item already exists in the wishlist
        item, item_created = WishListItem.objects.get_or_create(wishlist=created, product=variant)

        if item_created:
            messages.success(request, 'Item added to wishlist.')
        else:
            messages.warning(request, 'Item already exists in the wishlist.')
        return redirect('wishlist')
    else:
        messages.warning(request, 'You cannot add items to the wishlist without logging in.')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])    
    




def remove_to_wishlist(request, item_id):
    print('hloow wishlist',item_id)
    # varinat = ProductVariant.objects.get(id=item_id)
    # wishlist = WishList.objects.get(user=request.user)
    item = WishListItem.objects.get(id=item_id)
    print(item)

    # if item.exists():
    item.delete()
    return redirect ('wishlist')
    


from django.shortcuts import get_object_or_404

def update_quantity(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        # Get the CartItems object using get_object_or_404
        cart_item = get_object_or_404(CartItems, id=product_id)

        # Update the quantity and price
        cart_item.quantity = quantity
        cart_item.price = cart_item.product.sale_price * Decimal(quantity)

        # Save the changes to the database
        cart_item.save()

        carts = Cart.objects.get(user=request.user)

        # Calculate cart totals
        cart_total = carts.get_total_price()
        discount_coupon = carts.coupon.discount if carts.coupon else 0

        sub_total = total_discount = total_price = 0
        cart_items = CartItems.objects.filter(cart=carts)

        for item in cart_items:
            total = item.product.sale_price * item.quantity
            sub_total += total

            # Update the price of each item based on the quantity and discount
            item_price = item.product.discount_price if item.product.discount_price else item.product.sale_price
            item.price = item_price * item.quantity

            # Calculate the total discount
            if item.product.discount_price:
                total_discount += (item.product.sale_price - item.product.discount_price) * item.quantity

            # Add the updated item price to the total price
            total_price += item.price

        # Calculate the change amount (total price minus total discount)
        change_amount =  cart_total - total_discount - discount_coupon

        # Prepare the response data
        updated_cart_items = CartItems.objects.filter(cart=carts)
        cart_items_data = [{'id': item.id, 'quantity': item.quantity, 'price': str(item.price)} for item in updated_cart_items]

        response_data = {
            'success': True,
            'message': 'Quantity updated successfully!',
            'price': str(cart_item.price),
            'quantity': str(cart_item.quantity),
            'total_price': cart_total,
            'cart_items': cart_items_data,
          
            'total_discount': total_discount,
            'coupon_applied_total': 0,  # Make sure to add the coupon calculation logic here
            'change_amount': change_amount,
            'sub_total': total_price 
        }

        return JsonResponse(response_data)

    response_data = {
        'success': False,
        'message': 'Invalid request'
    }
    return JsonResponse(response_data, status=400)




def create_coupon(request):

    return render(request, 'admin_side/create_coupon.html')

def coupon_list(request):
    coupons = Coupon.objects.all().order_by('valid_from')

    return render(request, 'admin_side/coupon_list.html', {'coupons': coupons})

def add_coupon(request):

    if request.method == 'POST':
        code = request.POST['code']
        discount = float(request.POST['discount'])
        valid_from = request.POST['valid_from']
        valid_to = request.POST['valid_to']
        minimum_order_amount = float(request.POST.get('minimum_order_amount', 0))
        is_active = bool(request.POST.get('is_active', False))
        single_user_per_user = bool(request.POST.get('single_user_per_user', False))
        quantity = int(request.POST['quantity'])

        # Convert the valid_from and valid_to strings to datetime objects
        valid_from_datetime = timezone.datetime.fromisoformat(valid_from)
        valid_to_datetime = timezone.datetime.fromisoformat(valid_to)

        coupon = Coupon(
            code=code,
            discount=discount,
            valid_from=valid_from_datetime,
            valid_to=valid_to_datetime,
            minimum_order_amount=minimum_order_amount,
            is_active=is_active,
            single_user_per_user=single_user_per_user,
            quantity=quantity
        )
        coupon.save()

    return redirect('coupon_list')








