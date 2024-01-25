# chat/views.py
from django.shortcuts import render, redirect
from .models import Conversation, CONVERSATION_STATUS, User, Message
import json
from django.http.response import JsonResponse


def index(request):
    return render(request, "chat/index.html")

def room(request, conversation_id):
    is_customer = request.GET.get("is_customer", False)
    conversation_status = Conversation.objects.get(external_id=conversation_id).status
    is_resolved = conversation_status == CONVERSATION_STATUS[2][0]
    return render(request, "chat/room.html", {"conversation_id": conversation_id, "is_customer": is_customer, "is_resolved": is_resolved})

def resolve(request):
    email_id = request.GET.get("email_id")
    conversation_id = request.GET.get("conversation_id")
    Conversation.objects.filter(external_id=conversation_id).update(status=CONVERSATION_STATUS[2][0])
    return redirect("customer", email_id = email_id)

def create_chat_request(request):
    request.POST = json.loads(request.body.decode('utf-8'))
    email_id = request.POST.get("email_id")
    message = request.POST.get("message")
    customer = User.objects.get(email=email_id).customer
    conversation = Conversation.objects.create(customer_id=customer.user.id)
    message = Message.objects.create(sender=customer.user, text=message, conversation_id=conversation)
    return redirect("chat:room", conversation_id=conversation.external_id)

def get_all_messages(request):
    request.POST = json.loads(request.body.decode('utf-8'))
    conversation_id = request.POST.get("conversation_id")
    messages = Conversation.objects.get(external_id=conversation_id).messages.all().values("sender__name", "sender__email", "text", "created_at")
    messages = list(messages)
    for message in messages:
        message["created_at"] = message["created_at"].isoformat()
    return JsonResponse({"messages": messages})