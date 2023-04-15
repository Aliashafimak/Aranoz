from django.urls import path
from . import views

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('change_address/',views.change_address,name='change_address'),
    # path('payment_process/', views.payment_process, name='payment_process'),
    path('cod/', views.cod, name='cod'),
    path('payment_callback/', views.payment_callback, name='payment_callback'),
    # path('razorpay_payment/', views.razorpay_payment, name='razorpay_payment'),
]
