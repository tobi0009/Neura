from rest_framework import serializers
from .models import Assistant, KnowledgeBaseEntry
import re

class AssistantSerializer(serializers.ModelSerializer):
    """
    Serializer for Assistant model.
    Handles validation for tag_name and provides usage hints.
    """
    class Meta:
        model = Assistant
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def validate_tag_name(self, value):
        # Ensure tag_name is unique, valid, and user-friendly
        if not value:
            raise serializers.ValidationError("Tag name is required")
        if Assistant.objects.filter(tag_name=value).exists():
            raise serializers.ValidationError("This tag name is already taken. Please choose a different one.")
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Tag name can only contain letters, numbers, and underscores")
        if len(value) < 3:
            raise serializers.ValidationError("Tag name must be at least 3 characters long")
        if len(value) > 30:
            raise serializers.ValidationError("Tag name must be 30 characters or less")
        return value
    
    def to_representation(self, instance):
        # Add WhatsApp usage example to API output
        data = super().to_representation(instance)
        data['whatsapp_usage'] = f"@{instance.tag_name}: your question"
        return data


class KnowledgeBaseEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for KnowledgeBaseEntry model.
    """
    class Meta:
        model = KnowledgeBaseEntry
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']