from django.shortcuts import get_object_or_404, render, redirect
from userprofile.models import *
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from cart.models import Cart
from store.models import *

from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail,EmailMessage
from aa_shopy import settings
from django.template.loader import render_to_string
import re

# Create your views here.

def user_profile(request):
    user = request.user
    categories = Category.objects.all()

    try:
        addresses  = UserAddress.objects.filter(user=user)
    except ObjectDoesNotExist:
        addresses = None

    return render(request, 'user_profile/userprofile.html', {'addresses':addresses, "categories":categories})


def address_view(request):
    user = request.user

    try:
        addresses  = UserAddress.objects.filter(user=user)
    except ObjectDoesNotExist:
        addresses = None



    return render (request, 'user_profile/address_view.html', {'addresses':addresses})



def add_address(request):
    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        address_line_1 = request.POST.get('address1')
        address_line_2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('pincode')
        country = request.POST.get('country')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone')

        is_delivery_address = request.POST.get('is_delivery_address') == 'true'

        if is_delivery_address:
            UserAddress.objects.filter(user=request.user).update(is_delivery_address=False)

        address = UserAddress(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            postal_code=postal_code,
            city=city,
            state=state,
            country=country,
            is_delivery_address=is_delivery_address
        )
        address.save()
        messages.success(request, "Address added successfully.")

        # RETURN REDIRECT BACK TO THE PREVIOUS PAGE
        previous_page = request.session.get('previous_page')
        if previous_page:
            return redirect(previous_page)

    # Set the previous_page session variable before rendering the form page
    request.session['previous_page'] = request.META.get('HTTP_REFERER')

    return render(request, 'user_profile/add_address.html')

def edit_address(request, address_id):
    try:
        user_address = UserAddress.objects.get(id=address_id, user=request.user)
    except user_address.DoesNotExist:
        return HttpResponse('Address not found.')
     
    if request.method == 'POST':
        # Get form data from the request
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        address_line_1 = request.POST['address1']
        address_line_2 = request.POST['address2']
        city = request.POST['city']
        state = request.POST['state']
        postal_code = request.POST['pincode']
        country = request.POST['country']
        email = request.POST['email']
        phone_number = request.POST['phone']
        is_delivery_address = request.POST.get('is_delivery_address', False)

        if is_delivery_address:
            UserAddress.objects.filter(user=request.user, is_delivery_address=True).update(is_delivery_address=False)




        # Update the user address fields
        user_address.first_name = first_name
        user_address.last_name = last_name
        user_address.address_line_1 = address_line_1
        user_address.address_line_2 = address_line_2
        user_address.city = city
        user_address.state = state
        user_address.postal_code = postal_code
        user_address.country = country
        user_address.email = email
        user_address.phone_number = phone_number
        user_address.is_delivery_address = is_delivery_address

        # Save the updated user address
      
        user_address.save()
        messages.success(request, "Address Edited Successfully")
        return redirect('address_view')
    
    context = {
        'user_address':user_address,
        'address_id':address_id,
     }
    return render(request,'user_profile/edit_address.html', context)

def delete_address(request, address_id):

    try:
        user_address = UserAddress.objects.get(id=address_id, user=request.user)
        user_address.delete()
       
    except user_address.DoesNotExist:
        return HttpResponse('Address not found.')
    return redirect('address_view')



def choose_delivery_address(request, address_id):
    user = request.user
    address = get_object_or_404(UserAddress, id=address_id, user=user)
    UserAddress.objects.filter(user=user, is_delivery_address=True).update(is_delivery_address=False)
    address.is_delivery_address = True
    address.save()
    
    messages.success(request, 'Delivery address selected successfully.')

    if 'checkout_page' in request.META.get('HTTP_REFERER', ''):
        return redirect('checkout_page')
    
    return redirect('user_profile')

def password_reset(request):
        if request.method == 'POST':
            pass1 = request.POST.get('pass1')
            newpassword1 = request.POST.get('newpass1')
            newpassword2 = request.POST.get('newpass2')

            user = request.user
            

            if newpassword1 == newpassword2:
                # Use regex to check password criteria
                if re.match(r'^(?=.*[a-z])(?=.*\d)(?!.*\s)[A-Za-z\d]{8,}$', newpassword1):
                    if user.check_password(pass1):
                       
                        user.password = make_password(newpassword1)
                        user.save()
                        user = authenticate(username=user.username, password=pass1)
                        login(request, user)
                        esubject = "Password Changed - AA_SHOPY"
                        emessage = render_to_string('user_profile/verify/password_changed.html', {'name': request.user.username })
                        email = EmailMessage(
                            esubject,
                            emessage,
                            settings.EMAIL_HOST_USER,
                            [request.user.email],
                        )
                        email.fail_silently = True
                        email.send()
                        
                        messages.success(request, 'Password reset successful!')
                        return redirect('user_profile')
                    else:
                        messages.error(request, 'Current password is incorrect.')
                else:
                    messages.error(request, 'New password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, and one digit.')
            else:
                messages.error(request, 'New passwords do not match.')
       
            
        return render(request,'user_profile/reset_password.html')

from django.core.paginator import Paginator
def user_view_wallet(request):
    user = request.user
    try:
        wallet = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        # If the wallet doesn't exist, create one for the user
        wallet = Wallet.objects.create(user=user, balance=0)
        transactions = [] 
 

    # Fetch the transaction history for the user's wallet
    transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-date') 

    paginator = Paginator(transactions, 10) 

    page_number = request.GET.get('page')
    products_paginator = paginator.get_page(page_number)

    context = {
        'wallet':wallet,
        'transactions':products_paginator
    }

    return render(request, 'user_profile/view_wallet.html', context)