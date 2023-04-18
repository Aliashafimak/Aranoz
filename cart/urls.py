from django.urls import path
from . import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('add_wishlist/<int:product_id>/',views.add_wishlist,name='add_wishlist'),
    path('remove_wishlist_item/<int:product_id>/<int:wishlist_item_id>/', views.remove_wishlist_item, name='remove_wishlist_item'),
    path('checkout/', views.checkout, name="checkout"),
    path('apply_coupon/', views.apply_coupon, name="apply_coupon"),
    
    path('update_cart/', views.update_cart, name="update_cart"),

    # path('add_address/', views.add_address, name='add_address'),
]

