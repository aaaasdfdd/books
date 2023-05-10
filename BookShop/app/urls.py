from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place_order/', views.place_order, name='place_order'),
    path('order_confirmation/', views.order_confirmation, name='order_confirmation'),
    path('search/', views.search, name='search'),
    path('apply_discount/', views.apply_discount, name='apply_discount'),
    path('remove_discount/', views.remove_discount, name='remove_discount'),
    path('contact/', views.contact, name='contact'),
    path('contact_thankyou/', views.contact_thankyou, name='contact_thankyou'),
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:book_id>/', views.remove_from_cart, name='remove_from_cart'),
]
