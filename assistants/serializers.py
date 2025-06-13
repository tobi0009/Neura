from rest_framework import serializers
from .models import Assistant, KnowledgeBaseEntry
import re

class AssistantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assistant
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def validate_tag_name(self, value):
        """
        Validate tag_name field
        """
        if not value:
            raise serializers.ValidationError("Tag name is required")
        
        # Check if tag name is unique
        if Assistant.objects.filter(tag_name=value).exists():
            raise serializers.ValidationError("This tag name is already taken. Please choose a different one.")
        
        # Validate format (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Tag name can only contain letters, numbers, and underscores")
        
        # Check length
        if len(value) < 3:
            raise serializers.ValidationError("Tag name must be at least 3 characters long")
        
        if len(value) > 30:
            raise serializers.ValidationError("Tag name must be 30 characters or less")
        
        return value
    
    def to_representation(self, instance):
        """
        Add helpful information for the frontend
        """
        data = super().to_representation(instance)
        data['whatsapp_usage'] = f"@{instance.tag_name}: your question"
        return data


class KnowledgeBaseEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBaseEntry
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']