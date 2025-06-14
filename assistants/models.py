from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

User = get_user_model()

class Assistant(models.Model):
    PLATFORM_CHOICE = [
        ('whatsapp', 'WhatsApp')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assistants')
    name = models.CharField(max_length=100)
    tag_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICE, default='whatsapp')
    group_id = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class KnowledgeBaseEntry(models.Model):
    assistant = models.ForeignKey('Assistant', on_delete=models.CASCADE, related_name='knowledge_entries')
    content = models.TextField()
    embedding = ArrayField(models.FloatField(), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Show a preview of the content with the assistant's name
        return f"{self.assistant.name} - {self.content[:50]}"

