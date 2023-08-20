from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.utils.crypto import get_random_string      
from aa_shopy import settings
from django.core.mail import send_mail,EmailMessage
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from .tokens import generate_token

from django.http import  HttpResponseRedirect
from cart.models import *


# Create your views here.

def home(request):
    
    return render(request, 'home.html') 



def signin(request):
      
   if request.method == 'POST':
      username = request.POST["username"]
      pass1 = request.POST['pass1']

      user = authenticate(username = username, password = pass1)

      if user is not None :
        
         otp_store = get_random_string(length=5, allowed_chars='0123456789')
         request.session['otp'] = otp_store
         request.session['user_pk'] = user.pk
       


         subject = "OTP Confirmations"
         message = f"Your OTP is: {otp_store}"

         from_email = settings.EMAIL_HOST_USER
         to_list = [user.email]

         send_mail(subject, message, from_email,to_list, fail_silently = True )
         # login(request,user)
         # return redirect('home')

         return render(request,'otp_verification.html') 
      else :
        messages.error(request, "Username or Password incorrect")  
        return redirect('signin')
    
      
   return render(request,'signin.html')


def reset_password(request, uidb64, token):
    
    try:
      uid = force_str(urlsafe_base64_decode(uidb64))
      myuser = User.objects.get(pk=uid)
      request.session['user_pk'] = myuser.pk
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
      myuser = None
    if myuser is not None and generate_token.check_token(myuser, token):
      myuser.is_active = True
      myuser.save()
      return redirect('update_password')
    else:
      return render(request, 'verify/activation_failed.html')



def update_password(request):

    user_id = request.session.get('user_pk')
    
    if request.method == 'POST':
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']  
        user = User.objects.get(pk=user_id)
        
        if pass1 != pass2:
            messages.error(request, "Passwords do not match. Please make sure the passwords match.")
            return HttpResponseRedirect(request.META['HTTP_REFERER'])    
        
        new_password = pass1  # Use pass1 as the new password
        
        # Set the new password for the user and save the user
        user.set_password(new_password)
        user.save()
        
        # Authenticate the user with the new password
        authenticated_user = authenticate(username=user.username, password=new_password)
        if authenticated_user:
            login(request, authenticated_user)  # Log in the user
            
            # Clear the session variable to prevent reusing the link for password reset
            del request.session['user_pk']

            messages.success(request, "Password reset successful. You are now logged in.")
            return redirect('home')
        else:
            # Password authentication failed
            messages.error(request, "Failed to log in with the new password.")
            return redirect('login')  # Redirect to a login page with error message
    else:
        return render(request, 'user_profile/verify/reset_password.html')


def forget_password(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        try:
            user = User.objects.get(username=username)
            current_site = get_current_site(request)
            esubject = "Confirm Your Email @ AA_SHOPY"
            message = render_to_string('user_profile/verify/pass_verify.html', {
                    'name': user.username,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': generate_token.make_token(user)
                })

        
            email = EmailMessage(
                esubject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
            )
            email.fail_silently = True
            email.send()

            messages.success(request, "A link has been sent to your email. Please check your email to reset your password.")
        except User.DoesNotExist:
            messages.error(request, "Username not found. Please check the username and try again.")

    return render(request, 'user_profile/verify/forget_password.html')

def otp_login(request):
    if request.method == 'POST':
        stored_otp = request.session.get('otp')
        user_id = request.session.get('user_pk')
        entered_otp = request.POST['fotp']
        guest_cart_id = request.session.get('cart_id')
    

        if stored_otp == entered_otp:
            try:
                myuser = User.objects.get(id=user_id)
                login(request, myuser)

                if guest_cart_id:
                    try:
                        guest_cart = Cart.objects.get(id=guest_cart_id)
                      
                        user_cart, created = Cart.objects.get_or_create(user=myuser)
                      

                        for guest_item in guest_cart.cartitems_set.all():
                           
                            try:
                                user_item = CartItems.objects.get(cart=user_cart, product=guest_item.product)
                                available_stock = guest_item.product.stock - user_item.quantity
                                if guest_item.quantity <= available_stock:
                                    user_item.quantity += guest_item.quantity
                                    user_item.save()
                                else:
                                    messages.error(request, f"Requested quantity for '{guest_item.product}' exceeds available stock.")
                            except CartItems.DoesNotExist:
                                # Assuming product_variant is related to ProductVariant
                                product_variant = guest_item.product
                                CartItems.objects.create(
                                    cart=user_cart,
                                    product=product_variant,
                                    quantity=guest_item.quantity,
                                    price=product_variant.sale_price  # Using the sale_price field from ProductVariant
                                )
                                
                        guest_cart.delete()
                        del request.session['cart_id']
                    except Cart.DoesNotExist:
                        pass
                return redirect('home')
            except User.DoesNotExist:
                messages.error(request, 'User not found')
                return redirect('signin')
        else:
            messages.error(request, 'Invalid OTP')
            return redirect('signin')



from authentication.models import UserDetail

def signup(request):
   
   if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        phone_number = request.POST['phone_number']

        # if UserDetail.objects.filter(phone_number=phone_number).exists():
        #     messages.error(request, "Phone already taken")
        #     return redirect('signup')

        if pass1 == pass2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken")
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already taken")
                return redirect('signup')
            elif len(username) > 13:
                messages.error(request, "Username must be under 13 characters")
                return redirect('signup')
            elif len(pass1) < 5:
                messages.error(request, "Password must be at least 5 characters")
                return redirect('signup')
            elif not username.isalnum():
                messages.error(request, "Username must be alphanumeric")
                return redirect('signup')
            elif username.isdigit():
                messages.error(request, "Username cannot consist of only digits")
                return redirect('signup')
            
            else:
                myuser = User.objects.create_user(username,email,pass1)
                myuser.is_active = False
                myuser.save()

                user_detail = UserDetail.objects.create(user=myuser, phone_number=phone_number)
                user_detail.save()
                
                messages.success(request, "Your account has been successfully created. We have sent you a confirmation email, please confirm your email in order to activate your account.")

                # Welcome Email
                subject = "Welcome to AA-Shopy"
                message = "Hello " + myuser.username + "!! \n\n" + "Welcome to AA-Shopy!\n\nThank you for visiting our website. We have also sent you a confirmation email. Please confirm your email address in order to activate your account.\n\nThanking You,\nOur Team AA-shop"
                from_email = settings.EMAIL_HOST_USER
                to_list = [myuser.email]
                send_mail(subject, message, from_email, to_list, fail_silently=True)

                # Email Address Confirmation Email
                current_site = get_current_site(request)
                email_subject = "Confirm your email @ AA-Shopy Login!!"
                message2 = render_to_string('email_confirmation.html', {
                    'name': myuser.username,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
                    'token': generate_token.make_token(myuser)
                })

                email = EmailMessage(
                    email_subject,
                    message2,
                    from_email,
                    [myuser.email],
                )
                email.fail_silently = True
                email.send()

                return render(request, 'signin.html')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

   return render(request, 'signup.html')



def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')


def signout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Logged out successfully')
        return redirect('home')
    return redirect('signin')



from django.conf import settings
from .models import UserDetail
from twilio.rest import Client

def send_otp_sms(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        user_details = UserDetail.objects.filter(phone_number=phone_number)
        
        if user_details.exists():
            user = user_details.first()  
            user_id = user.user_id
            request.session['user_pk'] = user_id
          
            
            otp_code = get_random_string(length=5, allowed_chars='0123456789')
            request.session['otp'] = otp_code
            phone_number = "+91" + phone_number
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f'Your OTP code is: {otp_code}',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            return render(request, 'otp_verification.html')
        else:
            messages.error(request, 'User with this phone number not found')
    
    return render(request, 'user_profile/verify/mobile_otp.html')
