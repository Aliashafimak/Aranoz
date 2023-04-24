from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404 


from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from cart.models import *
from store.models import *
from .forms import AddressForm
from accounts.models import *
from .models import Coupon
from .forms import CouponForm
from datetime import datetime
from django.utils import timezone
now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
from pytz import timezone 
from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from .models import CartItem

# 
# def update_cart(request):
#     # Get the product ID, cart item ID, quantity, and price/total IDs from the AJAX request
#     product_id = request.POST.get('product_id')
#     cart_item_id = request.POST.get('cart_item_id')
#     quantity = request.POST.get('quantity')
#     price_id = request.POST.get('price_id')
#     total_id = request.POST.get('total_id')

#     # Get the cart item and product
#     cart_item = CartItem.objects.get(id=cart_item_id)
#     product = Product.objects.get(id=product_id)

#     # Update the cart item quantity and sub-total
#     cart_item.quantity = quantity
#     cart_item.sub_total = quantity * product.price
#     cart_item.save()

#     # Calculate the updated price and total for the cart item
#     updated_price = cart_item.product.price
#     updated_total = cart_item.sub_total

#     # Calculate the updated subtotal, tax, and grand total for the cart
#     cart_items = CartItem.objects.filter(cart_id=request.session['cart_id'])
#     subtotal = sum([item.sub_total for item in cart_items])
#     tax = subtotal * Decimal(0.1)
#     grand_total = subtotal + tax

    # Return the updated price and total for






def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    current_user = request.user
    
    
    product = Product.objects.get(id=product_id) #get the product
    #Delete from wishlist if exists
    try:
        wishlist_item = WishlistItem.objects.get(user=current_user,product=product)
        wishlist_item.delete()
    except WishlistItem.DoesNotExist:
        print("Wishlist item does not exist.")
    except Exception as e:
        print(f"An error occurred while deleting the wishlist item: {e}")

    # If the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except Variation.DoesNotExist:
    
                   print("Variation does not exist.")
                except Exception as e:
    
                    print(f"An error occurred while retrieving the variation: {e}")
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        print(is_cart_item_exists, 'is cart item exists bool==============================================================')
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            print(cart_item, 'cart item in existing cart item==============================================================')
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            print('==============================================cart item does not exist=============================')
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = request.user
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
    # If the user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass


        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing_variations -> database
            # current variation -> product_variation
            # item_id -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)


            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')


def remove_cart(request, product_id, cart_item_id):

    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        messages.error(request, 'This item is not in your cart.')
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0

    if request.user.is_authenticated:
        try:
            cart= Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=request.user)
            
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:
        cart_id = _cart_id(request)
        try:
            cart = Cart.objects.get(cart_id=cart_id)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=cart_id)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity

    tax = round((2 * total) / 100, 2)
    grand_total = round(total + tax, 2)

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'cart/cart.html', context)




#############################################CHECKOUT########################################################################################################################################
@login_required(login_url='login')
def checkout(request):
    try:
        tax = 0
        total= 0
        quantity = 0
        grand_total = 0
        discount_amount=0
        current_datetime = timezone.localtime(timezone.now())
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        
        # form = CouponForm()
        # if request.method == 'POST': 
        #     form = CouponForm(request.POST)
        #     if form.is_valid():
        #         code = form.cleaned_data['code']  

        discount_percent = request.session.get('discount_percent', 0)
            # print(discount_percent,'$$$$$$$$$$$$$$$$$$$$$$$discount_per$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')

        discount_amount= (total*discount_percent)/100
        totals= total+tax
            # apply discount amount to grand total
        grand_total = (totals- discount_amount )
        # else:
        #      grand_total=total+tax 

    except ObjectDoesNotExist:
        pass    

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        'current_datetime': current_datetime,
        'discount_amount' : discount_amount
    }
    return render(request, 'cart/checkout.html', context)



#################################################################################################################################################################

from django.shortcuts import redirect

def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('code')
        

       
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            
            if coupon.is_valid():
                discount_percent = coupon.discount
                request.session['discount_percent'] = float(discount_percent)
                user_coupon = UserCoupon(user=request.user, coupon=coupon)
                user_coupon.save()

                messages.success(request, "Coupon applied successfully!")
            else:
                messages.warning(request, "Coupon is not valid or has expired.")
        except ObjectDoesNotExist:
            messages.warning(request, "Invalid Coupon code.")
    return redirect('checkout')


########################################################WISHLIST#####################################################################################

def _wishlist_id(request):
    wishlist = request.session.session_key
    if not wishlist:
        wishlist = request.session.create()
    return wishlist

def add_wishlist(request,product_id):
  product = Product.objects.get(id=product_id)

  try:
    wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
  except Wishlist.DoesNotExist:
    wishlist =  Wishlist.objects.create(
      wishlist_id=_wishlist_id(request)
    )
    wishlist.save()

  try:
      wishlist_item = WishlistItem.objects.get(product=product,wishlist=wishlist)
  except WishlistItem.DoesNotExist:
      wishlist_item = WishlistItem.objects.create(
            product  = product,
            wishlist = wishlist,
        )
      wishlist_item.save()
  if request.user.is_authenticated:
    wishlist_item.user = request.user
    wishlist_item.save()

  return redirect(request.META['HTTP_REFERER'])



def wishlist(request,wishlist_items=None):

    try:
        wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist,is_active=True)
                
    except ObjectDoesNotExist:
        pass

    context = {
        'items' : wishlist_items
    }
    
    return render(request,'cart/wishlist.html',context)

def remove_wishlist_item(request, product_id, wishlist_item_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        
        if request.user.is_authenticated:
            wishlist_item = WishlistItem.objects.get(product=product, user=request.user, id=wishlist_item_id)
            
        else:
            wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
            wishlist_item = WishlistItem.objects.get(product=product, wishlist=wishlist, id=wishlist_item_id)
        wishlist_item.delete()
    except WishlistItem.DoesNotExist:

     messages.error(request, 'This item is not in your wishlist.')
    
    return redirect('wishlist')




#############################################################################################################################################################
# @login_required(login_url='login')
# def add_address(request):
#     form = AddressForm()
#     if request.method == 'POST':
#         # Get form data
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         company = request.POST.get('company')
#         phone_number = request.POST.get('phone_number')
#         email_address = request.POST.get('email_address')
#         address1 = request.POST.get('address1')
#         address2 = request.POST.get('address2')
#         city = request.POST.get('city')
#         zipcode = request.POST.get('zipcode')
#         order_note = request.POST.get('order_note')
        
#         # Create new Address object
#         address = Address(
#             user=request.user,
#             first_name=first_name,
#             last_name=last_name,
#             company=company,
#             phone_number=phone_number,
#             email_address=email_address,
#             address1=address1,
#             address2=address2,
#             city=city,
#             zipcode=zipcode,
#             order_note=order_note,
#         )
        
#         # # Set billing or shipping address based on address_type parameter
#         # if address_type == 'billing':
#         #     address.billing_address = True
#         # else:
#         #     address.billing_address = False
        
#         # # Save address object to database
#         # address.save()
        
#         # return redirect('address_list')
    
#     # Render the form template
#     context = {
#         # 'address_type': address_type,
#         'form': form
#     }
#     return render(request, 'cart/checkout.html', context)


               



