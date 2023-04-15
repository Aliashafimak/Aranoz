from django.db import models

#from django.db import models
from accounts.models import Account
from store.models import Product, Variation

# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    paymentId = models.CharField(max_length=100)
    amountPaid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    createdAt = models.DateTimeField(auto_now_add=True)
    paymentMethod = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.paymentId


status = (
    ('New' , 'New'),
    ('Order Confirmed', 'Order Confirmed'),
        ('Shipped',"Shipped"),
        ('Out for delivery',"Out for delivery"),
        ('Delivered', 'Delivered'),
        ('Cancelled','Cancelled'),
        ('Returned','Returned'),

    

)

class Order(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True , null=True)
    order_number = models.CharField(max_length=30)
    dateCreated = models.DateTimeField(auto_now_add=True)
    orderTotal = models.FloatField()
    tax = models.FloatField(default='18')
    status = models.CharField(choices=status, default='Order Confirmed', max_length=50)
    isOrdered = models.BooleanField(default=False)
    refund = models.CharField(max_length=100, blank=True, null=True, default=None)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email_address = models.EmailField(max_length=100, default='email')
    phone_number = models.CharField(max_length=100, default='phone')
    address1 = models.CharField(max_length=100, blank=True, null=True, default=None)
    address2 = models.CharField(max_length=100, blank=True, null=True, default=None)
    city = models.CharField(max_length=100)
    state = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=50)
    zipcode = models.IntegerField(null=True)
    is_returned = models.BooleanField(default=False)
    return_reason = models.CharField(max_length=50, blank=True)
    orderNote = models.TextField(max_length=1000, blank=True, null=True, default=None)

    createdAt = models.DateTimeField(auto_now=True)
    modifiedAt = models.DateTimeField(auto_now=True)

    def fullName(self):
        return f'{self.first_name} {self.last_name}'
    
    def fullAddress(self):
        return f'{self.address1} {self.address2} {self.city}{self.state}{self.country} {self.zipcode}'
    
    # def __str__(self):
    #     return self.firstName

    def __str__(self):
        return f'Order {self.id}'



class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete= models.CASCADE, null=True, blank=True)
    Payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    productPrice = models.FloatField(null=True, blank=True)
    ordered = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_name
