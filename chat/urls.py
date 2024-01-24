# chat/urls.py
from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    # path("", views.index, name="index"),
    path("resolve/", views.resolve, name="resolve"),
    path("<str:conversation_id>/", views.room, name="room"),
]
