from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("mail-order/", views.mail_order, name="mail_order"),
    path("<slug:c_slug>/", views.products_by_category, name="products_by_category"),
    path("<slug:c_slug>/<slug:p_slug>/", views.product_details, name="product_details"),
    path('cart-add/<int:id>', views.cart_add, name='cart_add'),
    path('cart-remove/<int:id>', views.cart_remove, name='cart_remove'),
    path('cart-clear/', views.cart_clear, name='cart_clear'),
]