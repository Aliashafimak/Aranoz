from django.db import models
from accounts.models import Account
from store.models import Product,Variation
from django.utils import timezone



# Create your models here.
class Cart(models.Model):
  cart_id = models.CharField(max_length=250, blank=True)
  date_added = models.DateField(auto_now_add=True)
  user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True,)  

  
  
  def __str__(self):
    return self.cart_id


class CartItem(models.Model):
  user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
  product =models.ForeignKey(Product, on_delete=models.CASCADE)
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
  variations = models.ManyToManyField(Variation, blank=True)
  quantity = models.IntegerField()
  is_active= models.BooleanField(default=True)
  price = models.IntegerField(default=1)
  
 
  
  def sub_total(self):
    
    return self.product.price * self.quantity
  




class Wishlist(models.Model):
  wishlist_id = models.CharField(max_length=250, blank=True)
  date_added = models.DateField(auto_now_add=True)
  
  def __str__(self):
    return self.wishlist_id

class WishlistItem(models.Model):
  user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  wishlist = models.ForeignKey(Wishlist,on_delete=models.CASCADE,null=True)
  is_active = models.BooleanField(default=True)
  cart_status = models.BooleanField(default=False)
  def __unicode__(self):
    return self.product  
  
  ################################################coupon##################################################################


class Coupon(models.Model):
    code = models.CharField(max_length=50)
    discount = models.DecimalField(max_digits=2, decimal_places=0)
    expiry = models.DateTimeField( blank=True, null=True)
    
    def __str__(self):
         return self.code
    
    def is_valid(self):
        now = timezone.now()
        return not (self.expiry and self.expiry < now)
    
class UserCoupon(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    coupon = models.ForeignKey( Coupon, on_delete=models.CASCADE)

    def __str__(self):
     return str(self.user)


     



 