from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("mail-order/", views.mail_order, name="mail_order"),
    path("category/<slug:slug>/", views.products_by_category, name="products_by_category"),
    path("product/<slug:slug>/", views.product_details, name="product_details"),
]