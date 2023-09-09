from django.urls import path
from .views import login, welcome, connect, product_list, webhooks, register_to_webhook, delete_webhook, details, create_product, delete, update, product_list_endpoint, single_product_endpoint

urlpatterns = [
    path("", login, name="login"),
    path("complete/", connect),
    path("welcome/", welcome, name="welcome"),
    path("webhooks/", webhooks, name="webhooks"),
    path("webhooks/register/", register_to_webhook, name="register_to_webhook"),
    path("webhooks/<int:id>/delete/", delete_webhook, name="delete_webhook"),
    path("product_list/", product_list, name="product_list"),
    path("<int:id>/", details, name="details"),
    path("<int:id>/update/", update, name="update"),
    path("create/", create_product, name="create_product"),
    path("<int:id>/delete/", delete, name="delete"),


    path("products/", product_list_endpoint, name="product_list_endpoint"),
    path("products/<int:id>/", single_product_endpoint, name="single_product_endpoint"),

]
