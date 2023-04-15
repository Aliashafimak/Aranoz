from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from order.models import Order,OrderProduct,Payment
from .models import *
from .forms import *
from django.contrib.auth import update_session_auth_hash
import random
from twilio.rest import Client
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from cart.models import CartItem,Cart
from cart.views import _cart_id
from cart.forms import AddressForm
from django.core.paginator import Paginator







def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # username = email.split("@")[0]
            username = form.cleaned_data['phone_number']
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()
            messages.success(request, 'Registration Suceesfull')

        

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address . Please verify it.')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
        # messages=messages.
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        print('=======user================================================')
        print(user)
        if user is not None:
            try:
                # Get the cart items for the cart
                cart_items = CartItem.objects.filter(cart=cart)
                if cart_items:

                    for item in cart_items:
                        item.user = user
                        item.save()

            except:
                pass


            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'accounts/login.html')









# Your Twilio account SID and auth token
account_sid = 'ACa73db4f018aae2b1e25a29ab7f233be3'
auth_token = '3fefbc51839e6e585fcaae1434148669'

# The phone number you purchased from Twilio
twilio_phone_number = '+15077044008'

def send_otp(phone_number, otp_code):
    client = Client(account_sid, auth_token)

    message = f"Your OTP code is: {otp_code}"

    # Send the message
    client.messages.create(
        body=message,
        from_=twilio_phone_number,
        to=phone_number
    )

def mobile_login(request):
    if request.method == 'POST':
        # Generate OTP and save to the database
        phone_number = request.POST['phone_number']
        otp_code = generate_otp()

        account = Account.objects.get(phone_number=phone_number)
        account.otp_code = otp_code
        account.save()

        # Send OTP via Twilio
        send_otp(phone_number, otp_code)

        # Render OTP input page
        context = {'phone_number': phone_number}
        return render(request, 'accounts/otp_input.html', context)

    # Render mobile number input page
    return render(request, 'accounts/mobile_login.html')


# from django.contrib.auth import authenticate, login

def otp_login(request):
    if request.method == 'POST':
        # Check OTP code and log in user
        otp_code = request.POST['otp_code']
        phone_number = request.POST['phone_number']
        account = Account.objects.get(phone_number=phone_number,otp_code=otp_code)
        otp=account.otp_code
        username = account.username
        # user = User.objects.get(username=username)
        
        password = account.password
        
        
        
        if otp_code == otp:
            # Authenticate the user and log them in
            user = auth.authenticate(username=username,password=password)
            
            if user is None:
                auth.login(request,account)
                return redirect('home')
            else:
                return redirect('login')

    # Render OTP input page again if OTP code is incorrect
    context = {'phone_number': phone_number, 'error_message': 'Invalid OTP code'}
    return render(request, 'accounts/otp_input.html', context)



def generate_otp():
    # Generate a 6-digit OTP code
    otp_code = random.randint(100000, 999999)
    return otp_code










@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
 

@login_required(login_url = 'login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


@login_required(login_url = 'login')
def addresscrud(request):
    addresses = Address.objects.filter(user=request.user)
    
    return render(request, 'accounts/addresscrud.html', {'addresses': addresses})

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(id=request.user.id)


        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                # auth.logout(request)
                messages.success(request, 'Password updated successfully')
                return redirect('dashboard')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')
def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')
    
@login_required(login_url='login')
def edit_profile(request):
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)



@login_required(login_url='userLogin')
def add_address(request):
    if request.method == 'POST':
        form = UserAddressForm(request.POST,request.FILES,)
        if form.is_valid():
            print('form is valid')
            address = Address()
            address.user = request.user
            address.address1 =  form.cleaned_data['address1']
            address.address2  = form.cleaned_data['address2']
            address.first_name  = form.cleaned_data['first_name']
            address.last_name  = form.cleaned_data['last_name']
            address.phone_number  = form.cleaned_data['phone_number']
            address.email_address  = form.cleaned_data['email_address']
            address.state =  form.cleaned_data['state']
            address.city =  form.cleaned_data['city']
            address.country = form.cleaned_data['country']
            address.zipcode =  form.cleaned_data['zipcode']
            address.save()
            messages.success(request,'Address added Successfully')
            return redirect('edit_profile')
        else:
            messages.success(request,'Form is Not valid')
            return redirect('add_address')
    else:
        form = UserAddressForm()
        context={
            'form':form
        }    
    return render(request,'accounts/add_address.html',context)

@login_required(login_url='login')
def delete_address(request,id):
    address=Address.objects.get(id = id)
    user = address.user
    addresses_of_user = Address.objects.filter(user=user).count()
    if addresses_of_user <= 1 :
      messages.error(request,"You cannot delete default address!")
      return redirect('addresscrud')
    else:
      messages.success(request,"Address Deleted")
      address.delete()
      return redirect('addresscrud')

#######################################################################################################################################################
@login_required(login_url='login')
def my_orders(request):
    all_orders = Order.objects.filter(user=request.user,isOrdered=True).order_by('-createdAt')
    
    paginator = Paginator(all_orders, 6)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)


    context = {
        'all_orders': page_object

    }
    print(all_orders.count())
    return render(request,'accounts/order_details.html',context)
#############################################################################################################################################################
@login_required(login_url='login')
def order_details(request,order_number):
    order_details = OrderProduct.objects.filter(order__order_number=order_number)
    order = Order.objects.get(order_number=order_number)
    subtotal = 0
    for order_product in order_details:
        subtotal += order_product.product.price * order_product.quantity

        
    context = {
        'order_details':order_details,
        'order':order,
        'subtotal':subtotal    
    }
    return render(request,'accounts/single_order_details.html',context)
##########################################################################################################################################################
def cancel_order(request,id):
    
    order = Order.objects.get(order_number = id,user = request.user)
    print(id,'$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$4')
    order.status = "Cancelled"
    order.save()
    # payment = Payment.objects.get(order_id = order.order_number)
    # payment.delete()

    return redirect('order_details', id)


##############################################################################################################################################################
# def return_order(request, id):
#   if request.method == 'POST':
#     return_reason = request.POST['return_reason']
#   print(return_reason)
#   order = Order.objects.get(order_number = id,user = request.user)
#   order.status = "Returned"
#   order.is_returned = True
#   order.return_reason = return_reason
#   order.save()
#   payment = Payment.objects.get(order_id = order.order_number)
#   payment.delete()
#   return redirect('order_details', id)

# def razorpay(request):
  
#   body = json.loads(request.body)
#   amount = body['amount']
      
#   amount = float(amount) * 100
  
#   DATA = {
#     "amount": amount,
#     "currency": "INR",
#     "receipt": "receipt#1",
#     "notes": {
#         "key1": "value3",
#         "key2": "value2"
#     }
#       }
#   payment = client.order.create(data=DATA)
#   return JsonResponse({
#     'payment':payment,
#      'payment_method' : "RazorPay"
#       })

