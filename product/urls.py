from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("mail-order/", views.mail_order, name="mail_order"),
    path("<slug:c_slug>/", views.products_by_category, name="products_by_category"),
    path("<slug:c_slug>/<slug:p_slug>/", views.product_details, name="product_details"),
]