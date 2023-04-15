from django.shortcuts import render, get_object_or_404
from category.models import Category
from store.models import Product
from django.db.models import Q
from django.core.paginator import EmptyPage, PageNotAnInteger,Paginator

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None: 
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator=Paginator(products,2)
        page =request.GET.get('page')#capture the page number that comes with the url
        paged_products=paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator=Paginator(products,6)
        page =request.GET.get('page')#capture the page number that comes with the url
        paged_products=paginator.get_page(page)#paged_products have 6 prducts
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/allproducts.html', context)


def sort_by_price(request):
    products = Product.objects.filter(is_available=True)
    product_count = products.count()

    # get the sorting parameter from the request
    sort_param = request.GET.get('sort')

    
    if sort_param == 'low_to_high':
        sortby = products.order_by('price')

    elif sort_param == 'high_to_low':
        sortby = products.order_by('-price') 
    else:
        sortby = products

    context = {
        'products': sortby,
        'sort_param': sort_param,
        'product_count':product_count,

    }     
    return render(request, 'store/allproducts.html', context)        






def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    context = {
        'single_product': single_product,
    }
    return render(request, 'store/product_detail.html',context)


def search(request):
  if request.method == 'GET':
    keyword= request.GET['keyword']
    if keyword:
      products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
      product_count = products.count()
      
  paginator = Paginator(products, 9)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
      
  context = {
    'products':page_obj,
    'product_count':product_count,
  }
  return render(request, 'store/allproducts.html', context)
