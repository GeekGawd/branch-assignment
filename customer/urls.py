# chat/urls.py
from django.urls import path

from . import views


urlpatterns = [
    path("", views.customer_form, name="customer-form"),
    path("<str:email_id>", views.customer, name="customer"),
]
