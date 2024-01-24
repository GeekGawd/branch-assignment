# chat/views.py
from django.shortcuts import render, redirect
from .models import Conversation, CONVERSATION_STATUS


def index(request):
    return render(request, "chat/index.html")

def room(request, conversation_id):
    is_customer = request.GET.get("is_customer", False)
    return render(request, "chat/room.html", {"conversation_id": conversation_id, "is_customer": is_customer})

def resolve(request):
    email_id = request.GET.get("email_id")
    conversation_id = request.GET.get("conversation_id")
    Conversation.objects.filter(external_id=conversation_id).update(status=CONVERSATION_STATUS[2][0])
    return redirect("customer", email_id = email_id)