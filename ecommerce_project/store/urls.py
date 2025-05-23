from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('products/', views.product_list_page, name='product_list_page'),
    path('product/<int:product_id>/', views.product_detail_page, name='product_detail_page'),
    path('cart/', views.view_cart_page, name='view_cart_page'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart_page'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart_page'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart_page'),
    path('checkout/', views.checkout_page, name='checkout_page'),
    path('order/success/<int:order_id>/', views.order_success_page, name='order_success_page'), # Updated
    path('account/profile/', views.user_profile_page, name='user_profile_page'),
    path('account/orders/', views.order_history_page, name='order_history_page'),
    path('account/addresses/', views.address_book_page, name='address_book_page'),
    path('account/addresses/set_default/<int:address_id>/', views.set_default_address, name='set_default_address'),
    path('account/addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),
]
