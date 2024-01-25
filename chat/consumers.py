# chat/consumers.py
import json
from .models import Conversation, User, Message
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from collections import defaultdict

CANNED_MESSAGES = {
    "greetings": [
        "Hi, I am the support agent. How can I help you?",
        "Welcome to Branch Support, How can I help you?",
        "Hello from Branch, Sorry to hear you are facing this issue, let me help you with this.",
    ],
    "ongoing": [
        "Sorry for the delay. I am looking into your case.",
        "Let me get the details of your case and get back to you.",
    ],
    "resolved": [
        "Thanks for contacting us. Have a great day!",
        "Branch is always here to help you. Have a great day!",
    ],
}


class ChatConsumer(AsyncWebsocketConsumer):
    room_connection_counts = defaultdict(lambda: 0)

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        return Conversation.objects.get(external_id=conversation_id)
    
    @database_sync_to_async
    def update_conversation(self, conversation_id, agent_active):
        return Conversation.objects.filter(external_id=conversation_id).update(agent_active=agent_active)

    @database_sync_to_async
    def get_all_messages(self, conversation_id):
        messages = Conversation.objects.get(external_id=conversation_id).messages.all().values("sender__name", "sender__email", "text", "created_at")
        messages = list(messages)
        for message in messages:
            message["created_at"] = message["created_at"].isoformat()
        return messages
    
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.room_name}"

        conversation = await self.get_conversation(self.room_name)

        self.room_connection_counts[self.room_name] += 1

        # If connection count is less than 2, and agent active is set true by mistake
        if self.room_connection_counts[self.room_name] <= 2:
            await self.update_conversation(self.room_name, False)
        
        conversation = await self.get_conversation(self.room_name)
        is_conversation_agent_active = conversation.agent_active
        
        if is_conversation_agent_active:
            await self.close(4000)
            return
        
        # Update the room to show that the agent is active
        await self.update_conversation(self.room_name, True)

        # Send past messages
        # messages = await self.get_all_messages(self.room_name)
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        canned_message_greetings = {
            "action": "canned_messages",
            "messages": CANNED_MESSAGES["greetings"],
        }
        
        await self.send(text_data=json.dumps(canned_message_greetings))

    async def disconnect(self, close_code):
        self.room_connection_counts[self.room_name] -= 1
        if close_code == 4000:
            await self.update_conversation(self.room_name, False)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get("action")

        if action == "chat_message":
            message = text_data_json.get("message")
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": text_data_json}
            )
    
    @database_sync_to_async
    def save_message_to_database(self, data):
        content = data["text"]
        sender_email = data["sender__email"]
        conversation_id = data["conversation_id"]

        sender = User.objects.get(email=sender_email)
        conversation = Conversation.objects.get(external_id=conversation_id)

        message = Message.objects.create(sender=sender, text=content, conversation_id=conversation)

        return message

    async def chat_message(self, event):
        message = event["message"]

        # Save message to database
        await self.save_message_to_database(message)

        # Send message to WebSocket
        await self.send(text_data=json.dumps([message]))

        # Evaluate message and send canned response
        if message["is_customer"] == "True":
            if "thank" in message["text"].lower() or "bye" in message["text"].lower():
                canned_message_resolved = {
                    "action": "canned_messages",
                    "messages": CANNED_MESSAGES["resolved"],
                }
                await self.send(text_data=json.dumps(canned_message_resolved))
            else:
                canned_message_ongoing = {
                    "action": "canned_messages",
                    "messages": CANNED_MESSAGES["ongoing"],
                }
                await self.send(text_data=json.dumps(canned_message_ongoing))