from django.contrib import admin

# Register your models here.
from .models import Order, OrderProduct ,Payment

# Register your models here.
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ['user', 'amountPaid','status', 'createdAt', 'paymentMethod']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'order_number', 'dateCreated', 'first_name', 'last_name','dateCreated',  'orderTotal', 'status', 'isOrdered', 'email_address', 'phone_number']
    list_editable = ['status', 'isOrdered']
    # list_filter = ['user', 'first_name', 'dateCreated', 'email_address', 'phone', 'orderTotal']
    list_per_page=15

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['order', 'Payment','user', 'product', 'quantity', 'ordered',]

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
admin.site.register(Payment,)