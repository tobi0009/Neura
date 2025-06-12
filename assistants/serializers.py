from rest_framework import serializers
from .models import Assistant, KnowledgeBaseEntry

class AssistantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assistant
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class KnowledgeBaseEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBaseEntry
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']