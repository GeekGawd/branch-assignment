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
        return self.name

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Conversation(Timestampable, UUIDable, models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.customer_name} -> {self.agent.name}"
    
class Message(Timestampable, UUIDable, models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_sender')
    text = models.TextField()
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    is_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.sender}->{self.conversation_id}->{self.text}"