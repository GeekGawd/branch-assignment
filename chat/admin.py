from django.contrib import admin
from .models import Agent, User, Conversation, Message, Customer

# Register your models here.

admin.site.register(Agent)
admin.site.register(User)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Customer)
