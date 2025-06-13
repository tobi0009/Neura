from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

User = get_user_model()

class Assistant(models.Model):
    """
    Represents a virtual assistant instance for a user.
    Each assistant can be linked to a specific platform (e.g., WhatsApp).
    """
    PLATFORM_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('discord', 'Discord'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assistants')  # Owner of the assistant
    name = models.CharField(max_length=100)  # Display name for the assistant
    tag_name = models.CharField(max_length=50, unique=True)  # Unique tag for mentions
    description = models.TextField(blank=True)  # Optional description
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)  # Platform type
    group_id = models.CharField(max_length=100, blank=True, null=True)  # Optional group/channel ID
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # Optional avatar image
    created_at = models.DateTimeField(auto_now_add=True)  # When assistant was created
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp

    def __str__(self):
        # Show assistant's name in admin and shell
        return self.name
    

class KnowledgeBaseEntry(models.Model):
    """
    Stores a single knowledge base entry for an assistant.
    Each entry can have an embedding for semantic search.
    """
    assistant = models.ForeignKey('Assistant', on_delete=models.CASCADE, related_name='knowledge_entries')
    content = models.TextField()  # The actual knowledge text
    embedding = ArrayField(models.FloatField(), blank=True, null=True)  # Vector for semantic search
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Show a preview of the content with the assistant's name
        return f"{self.assistant.name} - {self.content[:50]}"

