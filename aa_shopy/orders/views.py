from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
import razorpay
from django.conf import settings
from cart.models import *
from django.contrib import messages
from decimal import Decimal
from django.db.models import F, Sum
from userprofile.models import UserAddress
from orders.models import *
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required(login_url='signin')
def checkout_page(request):
    user = request.user
    cart = Cart.objects.get(user_id=user)
    cart_items = cart.cartitems_set.all()
    user_wallet = Wallet.objects.get(user=user)
    


    # Check if any address is selected as the delivery address
    selected_address = UserAddress.objects.filter(user=user, is_delivery_address=True).first()
    if not selected_address:
        messages.error(request, "Please add a delivery address.")
        return redirect('add_address')

    out_of_stock_products = [f"{item.product.product.name} - {item.product.color}" for item in cart_items if item.product.stock < item.quantity]

    if out_of_stock_products:
        error_message = ", ".join(out_of_stock_products) + " is out of stock. please remove them from your cart."

        messages.error(request, error_message)
        return redirect('cart')

    subtotal = cart_items.aggregate(subtotal=Sum('price'))['subtotal'] or Decimal('0.00')

    shipping_charge = Decimal('50') if subtotal< Decimal('1000') else Decimal('0.00')

    discount = Decimal(request.session.get('total_discount', '0.00'))

    total_prices = subtotal
    
    
    if cart and cart.coupon:
        
        coupon = get_object_or_404(Coupon, code=cart.coupon)
        print("coupon",coupon)
        min_amount = coupon.discount
        print(min_amount)
        total_prices = subtotal - min_amount
        print(total_prices)
    else:
        total_prices = subtotal



    total_price = total_prices + shipping_charge - discount 

    request.session['total_price'] = str(total_price)

    addresses = UserAddress.objects.filter(user=user)

    selected_address = addresses.filter(is_delivery_address=True).first()

    categories = Category.objects.all()
    

    context = {
        'cart':cart,
        'subtotal':subtotal,
        'shipping_charge':shipping_charge,
        'discount_amount':discount,
        'total_price':total_price,
        'cart_items':cart_items,
        'addresses':addresses,
        'selected_address':selected_address,
        'categories':categories,
        'user_wallet':user_wallet


    }

    return render (request, 'orders_folder/checkout.html', context)

from userprofile.models import *

def wallet_place_order(request, selected_address_id):
    user_address = get_object_or_404(UserAddress, id=selected_address_id, user=request.user)

    cart = Cart.objects.get(user_id=request.user)
    cart_items = cart.cartitems_set.all()
    
    # Convert total_price from session to Decimal
    total_price = Decimal(request.session.get('total_price', '0.00'))

    if not user_address:

        return redirect('checkout_page')

    user_wallet = Wallet.objects.get(user=request.user)

    if user_wallet.balance < total_price:
        
        messages.error(request, 'Insufficient wallet balance')
        return redirect(request.META.get('HTTP_REFERER'))

    
    user_wallet.balance -= total_price
    user_wallet.save()
    

    

    address_details = f"{user_address.first_name} {user_address.last_name}\n{user_address.address_line_1}\n"
    if user_address.address_line_2:
        address_details += f"{user_address.address_line_2}\n"
    address_details += f"{user_address.city}, {user_address.state} {user_address.postal_code}\n{user_address.country}"

    order = Order.objects.create(
        user=request.user,
        address=user_address,
        total_price=total_price,
        payment_status='PAID',
        payment_method='WALLET',
        address_details=address_details,
    )

    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            price=cart_item.price,
            quantity=cart_item.quantity
        )
        variant = cart_item.product
        variant.stock -= cart_item.quantity
        variant.save()
    cart_items.delete()

    transaction_type = 'Purchased'
    WalletTransaction.objects.create(wallet=user_wallet, amount=total_price, order_id=order, transaction_type=transaction_type)

    return render(request, 'orders_folder/order_placed.html')








def place_order(request, selected_address_id):    
         
    user_address = get_object_or_404(UserAddress, id=selected_address_id, user=request.user)
       

    cart = Cart.objects.get(user_id=request.user)
    cart_items = cart.cartitems_set.all()
    total_price = request.session.get('total_price', Decimal('0.00'))
        

    # Check if a delivery address is selected
    if not user_address:
        # Redirect to the checkout view with an error message indicating that no delivery address is selected
        return redirect('checkout_page')
    
    # Copy address details to a string and store them in the Order object
    address_details = f"{user_address.first_name} {user_address.last_name}\n{user_address.address_line_1}\n"
    if user_address.address_line_2:
        address_details += f"{user_address.address_line_2}\n"
    address_details += f"{user_address.city}, {user_address.state} {user_address.postal_code}\n{user_address.country}"

    order = Order.objects.create(
        user=request.user,
        address=user_address,
        # address=address_details,
        total_price=total_price,
        payment_status='ORDERED',
        payment_method='CASH_ON_DELIVERY',
        address_details=address_details,
            
    )

    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            price=cart_item.price,
            quantity=cart_item.quantity
        )

        variant = cart_item.product
        variant.stock -= cart_item.quantity
        variant.save()

    cart_items.delete()

    return render(request, 'orders_folder/order_placed.html')





# Razor pay function

def initiate_payment(request):

    if request.method == 'POST':
        # Retrieve the total price and other details from the backend
        cartss = Cart.objects.get(user=request.user)
        items = CartItems.objects.filter(cart=cartss)
    
        subtotal = items.aggregate(total_price=Sum('price'))['total_price'] or 0
        
        total_price = subtotal

        # if cartss and cartss.coupons:
        #     coupon = get_object_or_404(Coupon, coupon_code=cartss.coupons)
        #     min_amount = coupon.discount_price
        #     total_price = subtotal - min_amount

        # else:
        #     total_price = subtotal


        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        
        payment = client.order.create({

            'amount': int(total_price * 100),
              'currency': 'INR', 
              'payment_capture': 1
              
              })
       
    
        response_data = {
            'order_id': payment['id'],
            'amount': payment['amount'],
            'currency': payment['currency'],
            'key': settings.RAZOR_KEY_ID,

        }
        return JsonResponse(response_data)

    # Return an error response if the request method is not POST
    return JsonResponse({'error': 'Invalid requestmethod'})


# After the order establishing

def online_payment_order(request, userId):

    if request.method == 'POST':

        payment_id = request.POST.getlist('payment_id')[0]
        orderId = request.POST.getlist('orderId')[0]
        signature = request.POST.getlist('signature')[0]

        user_adds = UserAddress.objects.get(id=userId, user=request.user)
        cartss = Cart.objects.get(user=request.user)
        items = CartItems.objects.filter(cart=cartss)
       
        subtotal = items.aggregate(total_price=Sum('price'))['total_price'] or 0
    
        total_price = subtotal
        
        # if cartss and cartss.coupons:
        #     coupon = get_object_or_404(Coupon, coupon_code=cartss.coupons)
        #     min_amount = coupon.discount_price
        #     total_price = subtotal - min_amount
        # else:
        #     total_price = subtotal
    
        order = Order.objects.create(
            user=request.user,
            address=user_adds,
            total_price=total_price,
            payment_status='PAID',
            payment_method='RAZORPAY',
            
            razor_pay_payment_id=payment_id,
            razor_pay_payment_signature=signature,
            razor_pay_order_id = orderId,
        )
       
        # if cartss and cartss.coupons:
        #     coupon = get_object_or_404(Cart, user=request.user)
        #     couponss = Coupon.objects.get(coupon_code=coupon.coupons)
        #     Usercoupon.objects.create(
        #         user=request.user,
        #         coupon=couponss,
        #         used=True,
        #         total_price=total_price
        #     )
        #     coupon.coupons = None
        #     coupon.save()
        # else:
        # # Add any additional logic that should be executed when no coupon is used
        #     pass

        for cart_item in items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                price=cart_item.price,
                quantity=cart_item.quantity
                # Set other fields as necessary
            )

        variant = cart_item.product
        print('variant===>',variant)
        variant.stock -= cart_item.quantity
        variant.save()
        print('variant===>',variant)
        
        orderId = order.id
        items.delete()

        return JsonResponse({'message': 'Order placed successfully','orderId':orderId})
    else:
        # Handle invalid request method (GET, etc.)
        return JsonResponse({'error': 'Invalid requestmethod'})


def order_success(request):
    
    return render(request, 'orders_folder/order_placed.html')


from django.core.paginator import Paginator
def orders_list(request):

    user = request.user
    orders = Order.objects.filter(user=user).order_by('-id')

    paginator = Paginator(orders, 10) 

    page_number = request.GET.get('page')
    products_paginator = paginator.get_page(page_number)

    context={
        'orders':products_paginator
    }

    return render(request, 'orders_folder/orders_list.html', context)



def order_detail(request, order_id):

    order = get_object_or_404(Order, id=order_id)
    
    order_items = OrderItem.objects.filter(order=order)
    
    

    context={
        'order':order,
        'order_items':order_items
    }

    return render(request, 'orders_folder/order_detail.html', context)


from django.views.decorators.http import require_POST

@require_POST
def order_cancel(request, order_id):
    
   
    order = get_object_or_404(Order, id=order_id)
    
    if order.payment_status != 'CANCELLED':
        

        order_items = OrderItem.objects.filter(order=order)
        

        for item in order_items:
            variant = item.product
            variant.stock = variant.stock + item.quantity
            variant.save()


        order.payment_status = 'CANCELLED'
        order.save()
        Notifications.objects.create(order=order, action_required=order.payment_status)
        messages.success(request, 'Your order Cancelled, cash will be credited soon.')

    return redirect(request.META.get('HTTP_REFERER'))


 
    

