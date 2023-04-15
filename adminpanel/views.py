from django.shortcuts import render,redirect
from django.contrib import messages, auth
from django.contrib.auth import login, authenticate, logout
from .forms import *
from django.views.decorators.cache import never_cache
from accounts.models import *
from category.models import *
from store.models import *
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q

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




def admin_dashboard(request):
  return render(request,'adminpanel/admindashboard.html')


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