from django.urls import path
from . import views 


urlpatterns = [
path('', views.adminpanel, name="adminpanel"),
path('admin_dashboard/', views.admin_dashboard,name='admin_dashboard'),
path('dashboard/<slug:month>', views.admin_dashboard_monthwise,name='admin_dashboard_monthwise'),
path('admin_user_management',views.admin_user_management,name='admin_user_management'),
path('<int:id>/block_user/', views.block_user, name='block_user'),
path('<int:id>/edit_user_data/', views.edit_user_data, name='edit_user_data'),


path('admin_categories/',views.admin_categories,name='admin_categories'),
path('<str:category_slug>/edit_category',views.admin_edit_category,name='admin_edit_category'),
path('<str:category_slug>/delete_category',views.admin_delete_category,name='admin_delete_category'),
path('add_category',views.admin_add_category,name='admin_add_category'),


path('admin_products/', views.admin_products, name='admin_products'),
path('<int:id>/admin_delete_product/', views.admin_delete_product, name='admin_delete_product'),
path('<int:id>/admin_edit_product/', views.admin_edit_product, name='admin_edit_product'),
path('admin_add_product/', views.admin_add_product, name='admin_add_product'),
path('admin_sales_data',views.adminSalesData,name='adminSalesData'),
path('logout/', views.admin_logout, name='admin_logout'),



path('admin_orders/', views.adminOrders, name='adminOrders'),
path('admin_change_order/<int:id>',views.adminChangeOrder,name="adminChangeOrder"),
path('admin_coupons/',views.adminCoupons,name="adminCoupons"),
path('admin_add_coupon/',views.adminAddCoupon,name="adminAddCoupon"),
path('admin_edit_coupon/<int:id>/',views.adminEditCoupon,name="adminEditCoupon"),
path('admin_delete_coupon/<int:id>/',views.adminDeleteCoupon,name="adminDeleteCoupon"),




    ]

