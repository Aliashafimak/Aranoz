import datetime
import logging
import time
from django.http import HttpResponse
from django.shortcuts import render, redirect 
from cart.models import *
from .forms import OrderForm
from cart.models import *
from accounts.models import *
from cart import *
import random
from .models import *
from django.contrib.auth.decorators import login_required
from cart import utils
import razorpay
from django.views.decorators.csrf import csrf_exempt



def place_order(request, total=0, quantity=0):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    addresses = Address.objects.filter(user=request.user)
    
    
    
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    # grand_total = total + tax
    discount_percent = request.session.get('discount_percent', 0)
    

    discount_amount= (total*discount_percent)/100
    totals= total+tax
        # apply discount amount to grand total
    grand_total = (totals- discount_amount )

    order=None
    

    if request.method == 'POST':
        form = OrderForm(request.POST)#saving values from form
        if form.is_valid():  

            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone_number = form.cleaned_data['phone_number']
            data.email_address = form.cleaned_data['email_address']
            data.address1 = form.cleaned_data['address1']
            data.address2 = form.cleaned_data['address2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.zipcode = form.cleaned_data['zipcode']
            data.orderNote = form.cleaned_data['orderNote']
            data.orderTotal = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
        
            random_number= random.randint(1000, 9999)
            order_number = current_date + str(random_number)
            
            data.order_number = order_number

            request.session['order_number'] = data.order_number
            request.session['grand_total'] = grand_total
            
            data.save()

            razorpay_amount = grand_total * 100 

            order = Order.objects.get(user=current_user, isOrdered=False, order_number=order_number)
            client = razorpay.Client(auth=(ecommerce.settings.RAZOR_KEY_ID, ecommerce.settings.RAZOR_KEY_SECRET))                         # razorpay fund collecting     -------------------------------------------
            payment = client.order.create({'amount':razorpay_amount , 'currency': 'INR', 'payment_capture': 1 })
            order_id = payment['id']
            user_addresses = Address.objects.filter(user=request.user)

        context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'addresses':addresses ,
                'razorpay_amount':razorpay_amount,
                'payment':payment,
                'order_id': order_id,
                'user_addresses':user_addresses,
            }
        return render(request, 'order/payment.html',context )
    else:
        return redirect('checkout')


def change_address(request):
    return redirect('addresscrud')

# def payment_process(request):
#     if request.method == 'POST':
#         payment_method = request.POST.get('payment_method')
#         if payment_method == 'cod':
#             return redirect('cod')
#         elif payment_method == 'razorpay':
#             return redirect('razorpay')
#     return redirect('cart')  # Redirect to some other page if form not submitted
######################################################################################################################################################################



@login_required(login_url='login')
def cod(request):
    cart_items = CartItem.objects.filter(user = request.user)
    total = utils.total(cart_items) or 0
    quantity = utils.quantity(cart_items)
    tax = utils.tax(total)
    grand_total = utils.grand_total(total, tax)
     

    # saving payment
    payment = Payment(
        user = request.user,
        paymentMethod = 'COD',
        amountPaid = grand_total,
        status = 'captured',
        paymentId=f'{int(time.time())}{request.user.id}',
       
    )
    payment.save()
    
    # updating order table
    order_number = request.session.get('order_number', None)
    order = Order.objects.get(user=request.user, order_number = order_number)

    order.payment = payment

    order.isOrdered = True
    order.status = "Order Confirmed" 
    order.save()

    # # Moving Cart items in Order Table
    cart_items = CartItem.objects.filter(user = request.user)
    for item in cart_items:
        orderProduct = OrderProduct()
        orderProduct.order_id = order.id
        orderProduct.Payment = payment
        orderProduct.user = request.user
        orderProduct.product_id = item.product_id
        orderProduct.quantity = item.quantity
        orderProduct.productPrice = item.product.price
        orderProduct.ordered = True
        orderProduct.save()

        # # Reducing the quantity of items from Stock in warehouse
        product = Product.objects.get(id = item.product_id)
        product.stock -= item.quantity
        product.save()

    order = Order.objects.get(order_number = order_number)
    ordered_products = OrderProduct.objects.filter(order_id = order.id)
    total = utils.total(ordered_products)
    tax = utils.tax(total)
    grand_total = utils.grand_total(total, tax)

    context = {
        'order_number': order_number,
        'order': order,
        'cart_items': ordered_products,
        'grand_total' : grand_total,
        'payment' : payment,
        
    }

    # Clearing the cart
    CartItem.objects.filter(user= request.user).delete()

    return render(request, 'order/cod.html', context)
    
import ecommerce

# @csrf_exempt
# def razorpay_payment(request):
#     grand_total = request.session.get('grand_total', None)
#     if request.method == 'POST':
#         print('-------------------------------------------------------------------------------',grand_total)
#         amount = grand_total * 100     # multiplying with 100 because razorpay accepts amount in paisa instead of rupees
#         print('--------------------------------------------------------------------------------------------',amount)
#         client = client.order.create(auth=(ecommerce.settings.RAZOR_KEY_ID, ecommerce.settings.RAZOR_KEY_SECRET))
#         payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})

#         context = {
#             'payment' : payment
#         }
#         return render(request, 'order/payment.html', context)
#     return redirect('cart')
# @csrf_exempt
# def payment_callback(request):
#     if request.method == 'POST':
#         payment_id = request.POST.get('razorpay_payment_id')
#         client = razorpay.Client(auth=(ecommerce.settings.RAZOR_KEY_ID, ecommerce.settings.RAZOR_KEY_SECRET))
#         payment = client.payment.fetch(payment_id)
#         amount = payment['amount']
#         status = payment['status']

#         # print('-----------status-after-payment-redirect-to-callback',status)
#         # print('----------payment_id-form rzpay-server -redirect-to-callback', payment_id)
#         # print('-----------client-form rzpay-server after -redirect-to-callback',client)
#         # print('------------payment-form rzpay-server after -redirect-to-callback', payment)

#         if status == 'captured':
#             #saving this payment details
#             payment = Payment(
#                 user = request.user,
#                 payment_method = 'RazorPay',
#                 payment_id = payment_id,
#                 amount_paid = amount,
#                 status = status,
#             )
#             payment.save()
            
#             #updating order table
#             order_number = request.session.get('order_number', None)
#             order = Order.objects.get(user = request.user , order_number = order_number)

#             order.payment = payment
#             order.isOrdered = True
#             order.save()

#             #assigning ordered cart items to order product table
#             cart_items = CartItem.objects.filter(user = request.user)
#             for item in cart_items:
#                 orderProduct = OrderProduct()
#                 orderProduct.order_id = order.id
#                 orderProduct.payment = payment
#                 orderProduct.user = request.user
#                 orderProduct.product_id = item.product_id
#                 orderProduct.quantity = item.quantity
#                 orderProduct.product_price = item.product.price
#                 orderProduct.ordered = True
#                 orderProduct.save()

#                 # Reducing the quantity of items from Stock in warehouse
#                 product = Product.objects.get(id = item.product_id)
#                 product.stock -= item.quantity
#                 product.save()

#             order = Order.objects.get(order_number = order_number)
#             ordered_products = OrderProduct.objects.filter(order_id = order.id)
#             total = utils.total(ordered_products)
#             tax = utils.tax(total)
        
#             # print(type(grand_total))
#             payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})

#             context = {
#                 'order_number': order_number,
#                 'order': order,
#                 'cart_items': ordered_products,
#                 'order' : order,
#             }

#              # Clearing the cart
#             # CartItem.objects.filter(user=request.user).delete()
#         else:
#             pass
#         return render(request, 'order/razorpay.html', context)
#     else:
#         # Return an HTTP response with a bad request status code
#         return HttpResponse(status=400)


@csrf_exempt
def payment_callback(request):
    context = {}
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        client = razorpay.Client(auth=(ecommerce.settings.RAZOR_KEY_ID, ecommerce.settings.RAZOR_KEY_SECRET))
        payment = client.payment.fetch(payment_id)
        amount = payment['amount']
        status = payment['status']

        # print('-----------status-after-payment-redirect-to-callback',status)
        # print('----------payment_id-form rzpay-server -redirect-to-callback', payment_id)
        # print('-----------client-form rzpay-server after -redirect-to-callback',client)
        # print('------------payment-form rzpay-server after -redirect-to-callback', payment)

        if status == 'captured':
            #saving this payment details
            payment = Payment(
                user = request.user,
                paymentMethod = 'RazorPay',
                paymentId = payment_id,
                amountPaid = amount,
                status = status,
            )
            payment.save()
            
            #updating order table
            order_number = request.session.get('order_number', None)
            order = Order.objects.get(user = request.user , order_number = order_number)

            order.payment = payment
            order.isOrdered = True
            order.status = "Order Confirmed" 
            order.save()

            #assigning ordered cart items to order product table
            cart_items = CartItem.objects.filter(user = request.user)
            for item in cart_items:
                orderProduct = OrderProduct()
                orderProduct.order_id = order.id
                orderProduct.Payment = payment
                orderProduct.user = request.user
                orderProduct.product_id = item.product_id
                orderProduct.quantity = item.quantity
                orderProduct.productPrice = item.product.price
                orderProduct.ordered = True
                orderProduct.save()

                # Reducing the quantity of items from Stock in warehouse
                product = Product.objects.get(id = item.product_id)
                product.stock -= item.quantity
                product.save()
            
            grand_total = request.session.get('grand_total')
            order = Order.objects.get(order_number = order_number)
            ordered_products = OrderProduct.objects.filter(order_id = order.id)
            total = utils.total(ordered_products)
            tax = utils.tax(total)
            subtotal=grand_total-tax
        
            # print(type(grand_total))
            payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})

            context.update({
                'order_number': order_number,
                'order': order,
                'ordered_products': ordered_products,
                'cart_items': ordered_products,
                'payment':payment,
                'grand_total':grand_total,
                'subtotal':subtotal,

            })

            # Clearing the cart
            
            CartItem.objects.filter(user=request.user).delete()
            
        else:
            pass
    else:
        # Return an HTTP response with a bad request status code
        return HttpResponse(status=400)

    return render(request, 'order/razorpay.html', context)

    


