from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('register/', views.register, name='register'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('staff/products/', views.product_list_staff, name='product_list_staff'),
    path('staff/product/add/', views.product_create, name='product_create'),
    path('staff/product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('staff/product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('staff/orders/', views.order_list_staff, name='order_list_staff'),
    path('staff/order/<int:order_id>/update-status/', views.order_update_status, name='order_update_status'),
    path('profile/', views.profile, name='profile'),
]

