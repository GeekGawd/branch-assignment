from django.db import models
import uuid
from django.utils import timezone

class Timestampable(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UUIDable(models.Model):
    id = models.BigAutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True