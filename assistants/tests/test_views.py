from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from assistants.models import Assistant, KnowledgeBaseEntry
import json

class AssistantViewsTest(TestCase):
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
        
    def test_assistant_list_requires_authentication(self):
        """Test that assistant list requires authentication"""
        url = reverse('assistant-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_assistant_list_authenticated(self):
        """Test getting assistant list for authenticated user"""
        self.client.force_authenticate(user=self.user)
        url = reverse('assistant-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Assistant")
        
    def test_create_assistant(self):
        """Test creating a new assistant"""
        self.client.force_authenticate(user=self.user)
        url = reverse('assistant-list-create')
        data = {
            'name': 'New Assistant',
            'tag_name': 'new_assistant',
            'description': 'A new test assistant',
            'platform': 'whatsapp'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assistant.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Assistant')
        
    def test_assistant_detail(self):
        """Test getting assistant details"""
        self.client.force_authenticate(user=self.user)
        url = reverse('assistant-detail', kwargs={'pk': self.assistant.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Assistant")
        
    def test_assistant_detail_unauthorized(self):
        """Test that users can't access other users' assistants"""
        other_user = get_user_model().objects.create_user(
            email="other@example.com",
            first_name='othername',
            last_name="otherlastname",
            password="testpassword",
        )
        self.client.force_authenticate(user=other_user)
        
        url = reverse('assistant-detail', kwargs={'pk': self.assistant.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_update_assistant(self):
        """Test updating an assistant"""
        self.client.force_authenticate(user=self.user)
        url = reverse('assistant-detail', kwargs={'pk': self.assistant.pk})
        data = {
            'name': 'Updated Assistant',
            'tag_name': 'updated_assistant',
            'description': 'Updated description',
            'platform': 'whatsapp'
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Assistant')
        
    def test_delete_assistant(self):
        """Test deleting an assistant"""
        self.client.force_authenticate(user=self.user)
        url = reverse('assistant-detail', kwargs={'pk': self.assistant.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Assistant.objects.count(), 0)

class KnowledgeBaseEntryViewsTest(TestCase):
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
        self.entry = KnowledgeBaseEntry.objects.create(
            assistant=self.assistant,
            content="Test content"
        )
        
    def test_knowledge_base_list_requires_authentication(self):
        """Test that knowledge base list requires authentication"""
        url = reverse('knowledge-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_knowledge_base_list_with_assistant_filter(self):
        """Test getting knowledge base entries filtered by assistant"""
        self.client.force_authenticate(user=self.user)
        url = reverse('knowledge-list-create')
        response = self.client.get(url, {'assistant': self.assistant.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], "Test content")
        
    def test_create_knowledge_base_entry(self):
        """Test creating a new knowledge base entry"""
        self.client.force_authenticate(user=self.user)
        url = reverse('knowledge-list-create')
        data = {
            'assistant': self.assistant.id,
            'content': 'New content for the knowledge base'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(KnowledgeBaseEntry.objects.count(), 2)
        self.assertEqual(response.data['content'], 'New content for the knowledge base')
        
    def test_knowledge_base_detail(self):
        """Test getting knowledge base entry details"""
        self.client.force_authenticate(user=self.user)
        url = reverse('knowledge-detail', kwargs={'pk': self.entry.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], "Test content")

class AnswerQueryViewTest(TestCase):
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
        
    def test_answer_query_requires_authentication(self):
        """Test that answer query requires authentication"""
        url = reverse('answer_query')
        response = self.client.get(url, {'query': 'test question', 'assistant_id': self.assistant.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_answer_query_missing_parameters(self):
        """Test answer query with missing parameters"""
        self.client.force_authenticate(user=self.user)
        url = reverse('answer_query')
        
        # Test missing query
        response = self.client.get(url, {'assistant_id': self.assistant.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test missing assistant_id
        response = self.client.get(url, {'query': 'test question'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_answer_query_invalid_assistant(self):
        """Test answer query with invalid assistant ID"""
        self.client.force_authenticate(user=self.user)
        url = reverse('answer_query')
        response = self.client.get(url, {'query': 'test question', 'assistant_id': 999})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_answer_query_unauthorized_assistant(self):
        """Test answer query with assistant belonging to different user"""
        other_user = get_user_model().objects.create_user(
            email="other@example.com",
            first_name='othername',
            last_name="otherlastname",
            password="testpassword",
        )
        other_assistant = Assistant.objects.create(
            user=other_user,
            name="Other Assistant",
            tag_name="other_assistant",
            platform="whatsapp"
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('answer_query')
        response = self.client.get(url, {'query': 'test question', 'assistant_id': other_assistant.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
