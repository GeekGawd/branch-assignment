from django.db import models
from branch.behaviours import Timestampable, UUIDable

# Create your models here.

class User(Timestampable, UUIDable, models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    def __str__(self):
        return self.name

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.name

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

CONVERSATION_STATUS = (
    ('OPEN', 'open'),
    ('ONGOING', 'ongoing'),
    ('RESOLVED', 'resolved'),
)
class Conversation(Timestampable, UUIDable, models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    agent_active = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=CONVERSATION_STATUS, default=CONVERSATION_STATUS[0][0])

    def __str__(self):
        return f"{self.customer.user.name} -> {self.status}"
    
class Message(Timestampable, UUIDable, models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_sender')
    text = models.TextField()
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    is_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self) -> str:
        return f"{self.sender}->{self.conversation_id}->{self.text}"