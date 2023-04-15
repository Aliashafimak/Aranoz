from django.contrib import admin

# Register your models here.
from .models import Cart,CartItem,Coupon,UserCoupon,Wishlist


class CartItemAdmin(admin.ModelAdmin):
    list_display= ('user', 'product','cart')

class CartAdmin(admin.ModelAdmin):
    list_display =('user', 'cart_id','date_added')

class couponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'expiry')

class UserCouponAdmin(admin.ModelAdmin):
    list_display = ['user', 'coupon']

admin.site.register(Coupon, couponAdmin)
admin.site.register(UserCoupon, UserCouponAdmin)

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Wishlist)