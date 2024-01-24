import csv
from django.core.management.base import BaseCommand
from chat.models import User, Customer, Agent, Conversation, Message
from faker import Faker
from collections import defaultdict
from datetime import datetime

class Command(BaseCommand):
    help = 'Import chats from a CSV file'

    def handle(self, *args, **kwargs):
        file_path = r"/home/suyash/projects/Branch-Assignment/GeneralistRails_Project_MessageData.csv"

        faker = Faker()
        user_message_groups = defaultdict(list)

        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                user_id = row['User ID']
                user_message_groups[user_id].append(row)

        for user_id, messages in user_message_groups.items():
            # Generate a fake user
            fake_email = faker.email()
            user, created = User.objects.get_or_create(name=faker.name(), email=fake_email)

            # Create a customer linked to the user
            customer, created = Customer.objects.get_or_create(user=user)

            # Create a conversation for this user
            conversation = Conversation.objects.create(customer=customer, status='OPEN')

            # Create messages for the conversation
            for message_data in messages:
                timestamp = datetime.strptime(message_data['Timestamp (UTC)'], '%Y-%m-%d %H:%M:%S')
                Message.objects.create(
                    sender=user, 
                    text=message_data['Message Body'], 
                    conversation_id=conversation, 
                    created_at=timestamp
                )

        self.stdout.write(self.style.SUCCESS('Successfully imported chats and created fake users'))