"""
Tests for WhatsApp webhook and setup instructions endpoints.
Covers message parsing, error handling, and Gemini fallback.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from assistants.models import Assistant, KnowledgeBaseEntry
from unittest.mock import patch, MagicMock
import json

class WhatsAppWebhookTest(TestCase):
    """
    Test suite for WhatsApp webhook endpoint.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name='testname',
            last_name="testlastname",
            password="testpassword",
        )
        self.assistant = Assistant.objects.create(
            user=self.user,
            name="Test Assistant",
            tag_name="test_assistant",
            platform="whatsapp"
        )
        
    def test_webhook_no_message(self):
        """Test webhook with no message body"""
        url = reverse('whatsapp-webhook')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_webhook_invalid_format(self):
        """Test webhook with invalid message format"""
        url = reverse('whatsapp-webhook')
        data = {'Body': 'This is not in the correct format'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_webhook_missing_tag(self):
        """Test webhook with missing tag name"""
        url = reverse('whatsapp-webhook')
        data = {'Body': ': This is a question without a tag'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_webhook_missing_question(self):
        """Test webhook with missing question"""
        url = reverse('whatsapp-webhook')
        data = {'Body': '@test_assistant:'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_webhook_invalid_tag(self):
        """Test webhook with non-existent tag"""
        url = reverse('whatsapp-webhook')
        data = {'Body': '@nonexistent_tag: What is this?'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    @patch('assistants.semantic_search.find_best_match')
    @patch('assistants.gemini.ask_gemini')
    def test_webhook_semantic_match_found(self, mock_gemini, mock_find_best_match):
        """Test webhook when semantic search finds a good match"""
        # Mock semantic search to return a good match
        mock_entry = MagicMock()
        mock_entry.content = "This is the answer from knowledge base"
        mock_find_best_match.return_value = (mock_entry, 0.8)
        
        url = reverse('whatsapp-webhook')
        data = {'Body': '@test_assistant: What is the answer?'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('This is the answer from knowledge base', response.content.decode())
        mock_gemini.assert_not_called()  # Gemini should not be called
        
    @patch('assistants.semantic_search.find_best_match')
    @patch('assistants.semantic_search.find_top_matches_from_entries')
    @patch('assistants.gemini.ask_gemini')
    def test_webhook_gemini_fallback(self, mock_gemini, mock_find_top_matches, mock_find_best_match):
        """Test webhook when using Gemini fallback"""
        # Mock semantic search to return no good match
        mock_find_best_match.return_value = (None, 0.3)
        
        # Mock top matches for context
        mock_entry = MagicMock()
        mock_entry.content = "Context information"
        mock_find_top_matches.return_value = [(mock_entry, 0.6)]
        
        # Mock Gemini response
        mock_gemini.return_value = "This is the answer from Gemini"
        
        url = reverse('whatsapp-webhook')
        data = {'Body': '@test_assistant: What is the answer?'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('This is the answer from Gemini', response.content.decode())
        mock_gemini.assert_called_once()
        
    @patch('assistants.semantic_search.find_best_match')
    @patch('assistants.semantic_search.find_top_matches_from_entries')
    @patch('assistants.gemini.ask_gemini')
    def test_webhook_no_knowledge_base(self, mock_gemini, mock_find_top_matches, mock_find_best_match):
        """Test webhook when assistant has no knowledge base"""
        # Mock semantic search to return no good match
        mock_find_best_match.return_value = (None, 0.3)
        
        # Mock no top matches (empty knowledge base)
        mock_find_top_matches.return_value = []
        
        # Mock Gemini response
        mock_gemini.return_value = "This is the answer from Gemini"
        
        url = reverse('whatsapp-webhook')
        data = {'Body': '@test_assistant: What is the answer?'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('This is the answer from Gemini', response.content.decode())
        
    @patch('assistants.semantic_search.find_best_match')
    @patch('assistants.semantic_search.find_top_matches_from_entries')
    @patch('assistants.gemini.ask_gemini')
    def test_webhook_gemini_failure(self, mock_gemini, mock_find_top_matches, mock_find_best_match):
        """Test webhook when both semantic search and Gemini fail"""
        # Mock semantic search to return no good match
        mock_find_best_match.return_value = (None, 0.3)
        
        # Mock no top matches
        mock_find_top_matches.return_value = []
        
        # Mock Gemini to return None (failure)
        mock_gemini.return_value = None
        
        url = reverse('whatsapp-webhook')
        data = {'Body': '@test_assistant: What is the answer?'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Sorry, I don't have an answer for that yet", response.content.decode())
        
    def test_webhook_correct_format(self):
        """Test webhook with correct message format"""
        url = reverse('whatsapp-webhook')
        data = {'Body': '@test_assistant: What is the answer?'}
        
        with patch('assistants.semantic_search.find_best_match') as mock_find_best_match:
            with patch('assistants.gemini.ask_gemini') as mock_gemini:
                mock_find_best_match.return_value = (None, 0.3)
                mock_gemini.return_value = "Test response"
                
                response = self.client.post(url, data)
                
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn('Test response', response.content.decode())

class WhatsAppSetupInstructionsTest(TestCase):
    """
    Test suite for WhatsApp setup instructions endpoint.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name='testname',
            last_name="testlastname",
            password="testpassword",
        )
        self.assistant = Assistant.objects.create(
            user=self.user,
            name="Test Assistant",
            tag_name="test_assistant",
            description="A test assistant",
            platform="whatsapp"
        )
        
    def test_setup_instructions_success(self):
        """Test getting setup instructions for a valid assistant"""
        url = reverse('whatsapp-setup', kwargs={'assistant_id': self.assistant.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertEqual(data['assistant_name'], "Test Assistant")
        self.assertEqual(data['tag_name'], "test_assistant")
        self.assertIn('setup_steps', data)
        self.assertIn('usage_examples', data)
        self.assertIn('tips', data)
        
    def test_setup_instructions_invalid_assistant(self):
        """Test getting setup instructions for non-existent assistant"""
        url = reverse('whatsapp-setup', kwargs={'assistant_id': 999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Assistant not found")
        
    def test_setup_instructions_contains_tag_name(self):
        """Test that setup instructions include the correct tag name in examples"""
        url = reverse('whatsapp-setup', kwargs={'assistant_id': self.assistant.id})
        response = self.client.get(url)
        
        data = response.data
        self.assertIn(f"@{self.assistant.tag_name}:", data['setup_steps'][2])
        
        for example in data['usage_examples']:
            self.assertIn(f"@{self.assistant.tag_name}:", example)
