from django.urls import path
from . import views



urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('change_password/', views.change_password, name='change_password'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('mobile_login/', views.mobile_login, name='mobile_login'),
    path('otp_login/', views.otp_login, name='otp_login'),
    
    path('send_otp/', views.send_otp, name='send_otp'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('addresscrud/', views.addresscrud, name= 'addresscrud'),
    path('add_address/',views.add_address,name='add_address'),
    path('delete_address/<int:id>',views.delete_address,name='delete_address'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_details/<int:order_number>', views.order_details, name='order_details'),
    path("cancel_order/<int:id>/",views.cancel_order,name='cancel_order'),
    # path("return_order/<int:id>/", return_order, name='return_order'),
    
 ]  

