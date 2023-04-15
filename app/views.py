from django.shortcuts import render
from store.models import Product
from category.models import Category
import random

def home(request):
    products = Product.objects.all().filter(is_available=True)
    categories = Category.objects.all()
    all_products = Product.objects.all()
    random_products = random.sample(list(all_products), 5)
    print(random_products)
    context = {
        'products': products,
        'categories': categories,
        'random_products': random_products

    }
    return render(request, 'index.html', context)



