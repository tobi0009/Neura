"""
Unit tests for Assistant and KnowledgeBaseEntry models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant, KnowledgeBaseEntry

class AssistantModelTest(TestCase):
    """
    Tests for the Assistant model.
    """
    def setUp(self):
        # Create test data that will be used in multiple tests
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name='testname',
            last_name="testlastname",
            password="testpassword",
        )
        
    def test_create_assistant(self):
        """Test creating an assistant with all required fields"""
        assistant = Assistant.objects.create(
            user=self.user,
            name="Test Assistant",
            tag_name="test_assistant",
            description="A test assistant"
        )
        
        self.assertEqual(assistant.name, "Test Assistant")
        self.assertEqual(assistant.tag_name, "test_assistant")
        self.assertEqual(assistant.user, self.user)
        self.assertIsNotNone(assistant.created_at)
        self.assertIsNotNone(assistant.updated_at)
        
    def test_assistant_str_representation(self):
        """Test the string representation of Assistant model"""
        assistant = Assistant.objects.create(
            user=self.user,
            name="Test Assistant",
            tag_name="test_assistant"
        )
        
        # Check the actual string representation
        self.assertEqual(str(assistant), "Test Assistant")
        
    def test_assistant_tag_name_uniqueness(self):
        """Test that tag names are unique"""
        Assistant.objects.create(
            user=self.user,
            name="First Assistant",
            tag_name="unique_tag"
        )
        
        # Try to create another assistant with the same tag name
        with self.assertRaises(Exception):
            Assistant.objects.create(
                user=self.user,
                name="Second Assistant",
                tag_name="unique_tag"
            )

class KnowledgeBaseEntryModelTest(TestCase):
    """
    Tests for the KnowledgeBaseEntry model.
    """
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name='testname',
            last_name="testlastname",
            password="testpassword",
        )
        self.assistant = Assistant.objects.create(
            user=self.user,
            name="Test Assistant",
            tag_name="test_assistant"
        )
        
    def test_create_knowledge_base_entry(self):
        """Test creating a knowledge base entry"""
        entry = KnowledgeBaseEntry.objects.create(
            assistant=self.assistant,
            content="This is test content for the knowledge base."
        )
        
        
        self.assertEqual(entry.content, "This is test content for the knowledge base.")
        self.assertEqual(entry.assistant, self.assistant)
        self.assertIsNotNone(entry.created_at)
        self.assertIsNotNone(entry.updated_at)
        
    def test_knowledge_base_entry_str_representation(self):
        """Test the string representation of KnowledgeBaseEntry model"""
        entry = KnowledgeBaseEntry.objects.create(
            assistant=self.assistant,
            content="Test content"
        )
        
        self.assertEqual(str(entry), "Test Assistant - Test content")
        
    def test_knowledge_base_entry_embedding_field(self):
        """Test that embedding field can be null initially"""
        entry = KnowledgeBaseEntry.objects.create(
            assistant=self.assistant,
            content="Test content"
        )
        
        self.assertIsNone(entry.embedding)
        
        # Test setting embedding
        test_embedding = [0.1, 0.2, 0.3]
        entry.embedding = test_embedding
        entry.save()
        
        entry.refresh_from_db()
        self.assertEqual(entry.embedding, test_embedding)