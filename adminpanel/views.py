
from datetime import timedelta
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages, auth
from django.contrib.auth import login, authenticate, logout
from .forms import *
from django.views.decorators.cache import never_cache
from accounts.models import *
from category.models import *
from store.models import *
from order.models import *
import calendar
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.db.models import Sum
from cart.forms import CouponForm
import datetime
from datetime import date
from datetime import datetime




@never_cache
def adminpanel(request):
  if 'email' in request.session:
    return redirect('admin_dashboard')
    
  if request.method == 'POST':
    # form = LoginForm(request.POST)
    email = request.POST['email']
    password = request.POST['password']
    
    user = authenticate(email=email, password=password)
    
    if user is not None:
      if user.is_superadmin:
        request.session['email'] = email
        
        login(request, user)
        return redirect('admin_dashboard')
        
      else:
        messages.error(request, 'You are not autherized to access admin panel')
        return redirect('adminpanel')
    else:
      messages.error(request, 'Invalid login credentials')
      return redirect('adminpanel')
    
  form = LoginForm
  return render(request, 'adminpanel/adminlogin.html', {'form':form})



@staff_member_required(login_url = 'adminLogin')
def admin_dashboard(request):
  
    customers_count = Account.objects.filter(is_admin=False).count()
    orders_count = Order.objects.filter(isOrdered=True).count()
    product_count = Product.objects.filter(is_available=True).count()
    total_orders = Order.objects.filter(isOrdered=True).order_by('createdAt')
    first_order_date = total_orders[0].createdAt.date()
    total_sales = round(sum(list(map(lambda x : x.orderTotal,total_orders))),2)
    today = date.today()
    this_year = today.year
    this_month = today.month
    label_list = []
    line_data_list = []
    bar_data_list =  []
    month_list=[]
    for year in range(first_order_date.year,this_year+1) :
        month = this_month if year==this_year else 12
        month_list= month_list+(list(map(lambda x : calendar.month_abbr[x]+'-'+str(year),range(1,month+1))))[::-1]
    for year in range(2022,(this_year+1)):
        this_month = this_month if year==this_year else 12
        for month in range(1,(this_month+1)):
            month_wise_total_orders = Order.objects.filter(isOrdered=True,createdAt__year = year,createdAt__month=month,).order_by('createdAt').count()
            month_name = calendar.month_abbr[month]
            label_update = str(month_name)+ ' ' + str(year)
            label_list.append(label_update)
            line_data_list.append(month_wise_total_orders)
    for year in range(2022,(this_year+1)):
        for month in range(1,(this_month+1)):
            monthwise_orders = Order.objects.filter(isOrdered=True,createdAt__year = year,createdAt__month=month,)
            monthwise_sales  = round(sum(list(map(lambda x : x.orderTotal,monthwise_orders))),2)
            bar_data_list.append(monthwise_sales)
     
    context = {
        'total_customers' : customers_count,
        'total_orders'    : orders_count,
        'total_products'  : product_count,
        'total_sales'     : total_sales,
        'month_list'      : month_list,
        'line_labels'     : label_list,
        'line_data'       : line_data_list,
        'bar_data'        : bar_data_list
    }
    return render(request,'adminpanel/admindashboard.html',context)
    


@staff_member_required(login_url = 'adminLogin')
def admin_dashboard_monthwise(request,month):
    total_orders = Order.objects.filter(isOrdered=True).order_by('createdAt')
    first_order_date = total_orders[0].createdAt.date()
    taken_month = month
    selected_month = taken_month[:3]
    selected_year = taken_month[4:9]
    today = datetime.today()
    selected_month_num = datetime.strptime(selected_month, '%b').month
    month_range  =calendar.monthrange(int(selected_year),int(selected_month_num))[1]
    
    day = today.day if selected_year==today.year else month_range
    month = datetime.strptime(selected_month, '%b').month
    customers_count = Account.objects.filter(is_admin=False,date_joined__year= selected_year,date_joined__month=month).count()
    orders_count = Order.objects.filter(isOrdered=True,createdAt__year = selected_year,createdAt__month=month,).count()
    product_count = Product.objects.filter(is_available=True,created_date__year=selected_year,created_date__month=month).count()
    total_orders = Order.objects.filter(isOrdered=True,createdAt__year = selected_year,createdAt__month=month,).order_by('createdAt')
    
    total_sales = round(sum(list(map(lambda x : x.orderTotal,total_orders))),2)
    month_list=[]
    for year in range(first_order_date.year,today.year+1) :
        month = today.month if year==today.year else 12
        month_list= month_list+(list(map(lambda x : calendar.month_abbr[x]+'-'+str(year),range(1,month+1))))[::-1]
    # x= total_orders[0].createdAt.date().day
    order_count_per_day = []
    for day in range (1,(day+1)):
        day_order = Order.objects.filter(isOrdered=True,createdAt__year = selected_year,createdAt__month=selected_month_num, createdAt__day=day).count()
        order_count_per_day.append(day_order)
    days = list(range(1,day+1))
    sales_per_day =[]
    for day in range (1,(day+1)):
        day_order = Order.objects.filter(isOrdered=True,createdAt__year = selected_year,createdAt__month=selected_month_num, createdAt__day=day)
        day_sales = sum(list(map(lambda x : x.orderTotal,day_order)))
        sales_per_day.append(day_sales)

    context = {
        'total_customers' : customers_count,
        'total_orders'    : orders_count,
        'total_products'  : product_count,
        'total_sales'     : total_sales,
        'month_list'      : month_list,
        'selected_month'  : taken_month,
        'line_labels'     : days,
        'line_data'       : order_count_per_day,
        'bar_data'        : sales_per_day,
    }
    return render(request,'adminpanel/admindashboard.html',context)


# Admin User Management
@staff_member_required(login_url = 'adminpanel')
def admin_user_management(request):
  if request.method == 'POST':
    search_key = request.POST.get('search')
    users = Account.objects.filter(Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key) | Q(email__icontains=search_key),is_superadmin=False)
   #  paginator = Paginator(users, 5)
   #  page_number = request.GET.get('page')
   #  page_obj = paginator.get_page(page_number)
  else:
    users = Account.objects.all().filter(is_superadmin=False).order_by('-id')
   #  paginator = Paginator(users, 10)
   #  page_number = request.GET.get('page')
   #  page_obj = paginator.get_page(page_number)
    
  context = {
    'users': users
  }
  return render(request,'adminpanel/user_management/admin_user_management.html',context)

@staff_member_required(login_url = 'adminpanel')
def block_user(request, id):
    users = Account.objects.get(id=id)
    if users.is_active:
        users.is_active = False
        users.save()

    else:
         users.is_active = True
         users.save()

    return redirect('admin_user_management')



@staff_member_required(login_url = 'adminpanel')
def edit_user_data(request, id):
  user = Account.objects.get(id=id)
  
  if request.method == 'POST':
    form = UserForm(request.POST, request.FILES, instance=user)
    if form.is_valid():
      form.save()
      messages.success(request, 'User Account edited successfully.')
      return redirect('admin_user_management')
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('edit_user_data', id)  
  else:
    form = UserForm(instance=user)
  context = {
    'form':form,
    'id':id,
  } 
  return render(request, 'adminpanel/user_management/edit_user_data.html', context)




# Admin Category Management
@staff_member_required(login_url = 'adminpanel')
def admin_categories(request):
  categories = Category.objects.all().order_by('id')
  
#   paginator = Paginator(categories, 10)
#   page_number = request.GET.get('page')
#   page_obj = paginator.get_page(page_number)
  
  context = {
    'categories':categories
  }
  return render(request, 'adminpanel/category_management/admin_categories.html', context)

@staff_member_required(login_url = 'adminpanel')
def admin_add_category(request):
  if request.method == 'POST':
    form = CategoryForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request, 'Category added successfully.')
      return redirect('admin_categories')
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('admin_add_category')
  else:
    form = CategoryForm()
    context = {
      'form':form,
    }
    return render(request, 'adminpanel/category_management/admin_add_category.html', context)
  
@staff_member_required(login_url = 'adminpanel')
def admin_edit_category(request, category_slug):
  category = Category.objects.get(slug=category_slug)
  
  if request.method == 'POST':
    form = CategoryForm(request.POST, request.FILES, instance=category)
    
    if form.is_valid():
      form.save()
      messages.success(request, 'Category edited successfully.')
      return redirect('admin_categories')
    else:
      messages.error(request, 'Invalid input')
      return redirect('admin_edit_category', category_slug)
      
  form =   CategoryForm(instance=category)
  context = {
    'form':form,
    'category':category,
  }
  return render(request, 'adminpanel/category_management/admin_edit_category.html', context)
  
@staff_member_required(login_url = 'adminpanel')  
def admin_delete_category(request, category_slug):
  category = Category.objects.get(slug=category_slug)
  category.delete()
  messages.success(request, 'Category deleted successfully.')
  return redirect('admin_categories')




# Product management
  
@staff_member_required(login_url = 'adminpanel')
def admin_products(request):
  if request.method == 'POST':
    search_key = request.POST.get('search')
    products = Product.objects.filter(Q(product_name__icontains=search_key))
   #  paginator = Paginator(products, 10)
   #  page_number = request.GET.get('page')
   #  page_obj = paginator.get_page(page_number)
  else:
    products = Product.objects.all().order_by('-id')
   #  paginator = Paginator(products, 10)
   #  page_number = request.GET.get('page')
   #  page_obj = paginator.get_page(page_number)
  
  context = {
    'products': products
  }
  return render(request, 'adminpanel/product_management/admin_products.html', context)

@staff_member_required(login_url = 'adminpanel')
def admin_add_product(request):
  if request.method == 'POST':
    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request, 'Product added successfully.')
      return redirect('admin_products')
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('admin_add_product')
  else:
    form = ProductForm()
    context = {
      'form':form,
    }
    return render(request, 'adminpanel/product_management/admin_add_product.html', context)

@staff_member_required(login_url = 'adminpanel')
def admin_edit_product(request, id):
  product = Product.objects.get(id=id)
  
  if request.method == 'POST':
    form = ProductForm(request.POST, request.FILES, instance=product)
    
    if form.is_valid():
      form.save()
      messages.success(request, 'product data edited successfully.')
      return redirect('admin_products')
    else:
      messages.error(request, 'Invalid parameters')
      
  form =   ProductForm(instance=product)
  context = {
    'form':form,
    'product':product,
  }
  return render(request, 'adminpanel/product_management/admin_edit_product.html', context)

@staff_member_required(login_url = 'adminpanel')  
def admin_delete_product(request, id):
  product = Product.objects.get(id=id)
  product.delete()
  return redirect('admin_products')


#logout
@staff_member_required(login_url='adminpanel')
def admin_logout(request):
    if 'email' in request.session:
        request.session.flush()
    auth.logout(request)
    messages.success(request, "You are logged out.")
    return redirect('adminpanel')


@staff_member_required(login_url= 'adminLogin')
def adminSalesData(request):
    total_orders = Order.objects.filter(isOrdered=True).order_by('createdAt')
    first_order_date = total_orders[0].createdAt.date()
    today = timezone.now()
    day = today.day
    month = today.month
    year = today.year
    month_list = []
    for i in range(1,13):month_list.append(calendar.month_name[i]) 
    year_list = []
    for i in range(first_order_date.year,year+1):year_list.append(i)
    this_date=str(today.date())
    start_date=this_date
    end_date=this_date
    filter= False
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        temp = start_date
        end_date = request.POST.get('end_date')
        # converting from naive to timezone aware
        # val = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
      
        val = timezone.make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d'))

        start_date = timezone.make_aware(datetime.strptime(temp, '%Y-%m-%d'))
        end_date = val+timedelta(days=1)
        filter=True
        orders = None
  # for orders within a date range
        orders = OrderProduct.objects.filter(order__createdAt__range=(start_date, end_date)).values( 'product__product_name', 'product__stock').annotate(total=Sum('productPrice'),dcount=Sum('quantity')).order_by('-total')
    else:
# for orders within a specific month and year
       orders = OrderProduct.objects.filter(order__createdAt__year=year,order__createdAt__month=month).values('product__product_name', 'product__stock').annotate(total=Sum('productPrice'),dcount=Sum('quantity')).order_by('-total')

# Now you can safely reference the `orders` variable outside of the `try` block

    # else:
        # orders = Order.objects.filter(createdAt__year = year,createdAt__month=month).values('user_order_page__product__product_name','user_order_page__product__stock',total = Sum('orderTotal'),).annotate(dcount=Sum('user_order_page__quantity')).order_by('-total')

    context = {
        'month_list':month_list,
        'orders':orders,
        'this_date':this_date,
        'year_list':year_list,
        'start_date':start_date,
        'end_date':end_date,
        'filter':filter
    }
    return render(request, 'adminpanel/adminSalesData.html', context)



@staff_member_required(login_url = 'adminLogin')
def adminOrders(request):
  orders = Order.objects.filter(isOrdered=True).order_by('-id')
  paginator = Paginator(orders, 10)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  
  context = {
    'orders':page_obj,
  }
  return render(request, 'adminpanel/orderManagement/adminOrders.html', context)


@staff_member_required(login_url = 'adminLogin')
def adminChangeOrder(request, id):
  if request.method == 'POST':
    order = get_object_or_404(Order, id=id)
    status = request.POST.get('status')
    order.status = status 
    order.save()
    if status  == "Delivered":
      try:
          payment = Payment.objects.get(payment_id = order.order_number, status = False)
          if payment.payment_method == 'Cash On Delivery':
              payment.status = True
              payment.save()
      except Payment.DoesNotExist:
        # Handle the case where the payment doesn't exist
        # or has already been marked as paid.
        print(f"Payment with ID {order.order_number} does not exist or has already been marked as paid.")
      except Exception as e:
        # Handle any other exceptions that may occur.
        print(f"An error occurred while processing payment for order {order.order_number}: {e}")
  return redirect('adminOrders')


@staff_member_required(login_url = 'adminLogin')
def adminCoupons(request):
  coupons = Coupon.objects.all()
  context = {
    'coupons':coupons,
  }
  return render(request, 'adminpanel/couponManagement/adminCoupons.html', context)


@staff_member_required(login_url = 'adminLogin')
def adminAddCoupon(request):
    form = CouponForm()
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save()
            messages.success(request, 'Coupon added successfully.')
            return redirect('adminCoupons')
        else:
            messages.error(request, 'Invalid input!!!')
            # no need to redirect to 'adminAddCoupon' - the form with errors will be displayed
    context = {
        'form':form,
    }
    return render(request, 'adminpanel/couponManagement/adminAddCoupon.html', context)



@staff_member_required(login_url='adminLogin')
def adminEditCoupon(request, id):
    coupon = Coupon.objects.get(id=id)
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon.code = form.cleaned_data['code']
            coupon.discount = form.cleaned_data['discount']
            coupon.expiry = form.cleaned_data['expiry']
            coupon.save()
            messages.success(request, 'Coupon updated successfully')
            return redirect('adminCoupons')
        else:
            messages.error(request, 'Invalid input!!!')
    else:
        form = CouponForm(initial={
            'code': coupon.code,
            'discount': coupon.discount,
            'expiry': coupon.expiry,
        })
    context = {
        'coupon': coupon,
        'form': form,
    }
    return render(request, 'adminpanel/couponManagement/adminEditCoupon.html', context)



@staff_member_required(login_url= 'adminLogin')
def adminDeleteCoupon(request, id):
  coupon = Coupon.objects.get(id = id)
  coupon.delete()
  messages.success(request,'Coupon deleted successfully')
  return redirect('adminCoupons')
