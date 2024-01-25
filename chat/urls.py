# chat/urls.py
from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    # path("", views.index, name="index"),
    path("resolve/", views.resolve, name="resolve"),
    path("create/", views.create_chat_request, name="create-chat-request"),
    path("messages/", views.get_all_messages, name="get-all-messages"),
    path("<str:conversation_id>/", views.room, name="room"),
]
