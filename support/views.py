from django.shortcuts import render, redirect
from chat.models import Conversation, Message, Agent, User, Customer, CONVERSATION_STATUS
from django.db.models import Subquery, OuterRef
from django.contrib import messages
from django.contrib.postgres.search import TrigramSimilarity, SearchVector
from django.db.models import F


# Create your views here.

def customer_form(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        user, created = User.objects.get_or_create(name=name, email=email)
        if created:
            Customer.objects.create(user=user)
        return redirect('customer', email_id=email)
    return render(request, "chat/customer_form.html")

def customer(request, email_id):
    first_message_subquery = Message.objects.filter(
        conversation_id=OuterRef('pk')
    ).order_by('created_at')

    open_support_requests = Conversation.objects.filter(customer__user__email=email_id).exclude(status=CONVERSATION_STATUS[2][0]).annotate(
        first_message=Subquery(first_message_subquery.values('text')[:1])
    )

    resolved_support_requests = Conversation.objects.filter(customer__user__email=email_id, status=CONVERSATION_STATUS[2][0]).annotate(
        first_message=Subquery(first_message_subquery.values('text')[:1])
    )

    return render(request, "chat/customer.html", {"email_id": email_id, "resolved_support_requests": resolved_support_requests, "open_support_requests": open_support_requests})

def agent_form(request):
    if request.method == "POST":
        email = request.POST.get('email')
        is_agent_exists = Agent.objects.filter(user__email=email).exists()
        if not is_agent_exists:
            messages.error(request, 'Agent with this email does not exist.')
            return render(request, "chat/agent_form.html")
        return redirect('agent', email_id=email)
    return render(request, "chat/agent_form.html")

def agent(request, email_id):
    search_query = request.GET.get('search', None)

    first_message_subquery = Message.objects.filter(
        conversation_id=OuterRef('pk')
    ).order_by('created_at')
    

    # Available conversations would be those where the agents are inactive
    available_support_requests = Conversation.objects.filter(agent_active=False).annotate(
        first_message=Subquery(first_message_subquery.values('text')[:1])
    )

    if search_query:
        trigram_queryset = available_support_requests.annotate(
            similarity=TrigramSimilarity('messages__text', search_query)
        ).filter(similarity__gt=0.07).order_by('-similarity')

        # print(trigram_queryset.values_list())

        vector_queryset = available_support_requests.annotate(
            search=SearchVector('customer__user__name', 'customer__user__email', 'messages__text')
        ).filter(search=search_query)

        search_queryset = available_support_requests.filter(messages__text__search=search_query)

        icontains_queryset = available_support_requests.filter(messages__text__icontains=search_query)

        # Combine QuerySets
        combined_queryset = list(vector_queryset) + list(search_queryset) + list(icontains_queryset) + list(trigram_queryset)

        # Remove duplicates if needed
        available_support_requests = list(set(combined_queryset))

    return render(request, "chat/agent.html", {"email_id": email_id, "support_requests": available_support_requests})