# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("customer/", views.customer_form, name="customer-form"),
    path("customer/<str:email_id>", views.customer, name="customer"),
    path("agent/", views.agent_form, name="agent-form"),
    path("agent/<str:email_id>", views.agent, name="agent"),
]
