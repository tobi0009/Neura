from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import KnowledgeBaseEntry
from sentence_transformers import SentenceTransformer
import threading
from .utils import get_model

# Signal runs after a KnowledgeBase object is saved
@receiver(post_save, sender=KnowledgeBaseEntry)
def generate_embedding(sender, instance, created, **kwargs):
    if created and not instance.embedding:
        # Threading to avoid blocking the request
        def process_embedding():
            model = get_model()
            embedding = model.encode(instance.content).tolist()  # Convert numpy array to list
            instance.embedding = embedding
            instance.save(update_fields=['embedding'])  # Save only the embedding field

        threading.Thread(target=process_embedding).start()
