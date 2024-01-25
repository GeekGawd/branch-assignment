# your_app/management/commands/update_search_vectors.py
from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from chat.models import User, Message

class Command(BaseCommand):
    help = 'Updates the search vectors for User and Message models.'

    def handle(self, *args, **kwargs):
        # Update search vector for User
        User.objects.update(name_email_vector=SearchVector('name', 'email'))

        # Update search vector for Message
        Message.objects.update(text_vector=SearchVector('text'))

        self.stdout.write(self.style.SUCCESS('Successfully updated search vectors.'))
