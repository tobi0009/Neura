from django.test import TestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant, KnowledgeBaseEntry
from assistants.semantic_search import find_best_match, find_top_matches, find_top_matches_from_entries
from unittest.mock import patch, MagicMock
import numpy as np

class SemanticSearchTest(TestCase):
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
            tag_name="test_assistant",
            platform="whatsapp"
        )
        
        # Create test knowledge base entries
        self.entry1 = KnowledgeBaseEntry.objects.create(
            assistant=self.assistant,
            content="Our business hours are Monday to Friday, 9 AM to 5 PM."
        )
        
        self.entry2 = KnowledgeBaseEntry.objects.create(
            assistant=self.assistant,
            content="You can contact us at support@example.com or call 555-0123."
        )
        
        self.entry3 = KnowledgeBaseEntry.objects.create(
            assistant=self.assistant,
            content="We offer consulting services, training programs, and technical support."
        )
        
    @patch('assistants.semantic_search.get_embedding')
    def test_find_best_match_with_embeddings(self, mock_get_embedding):
        """Test finding best match when entries have embeddings"""
        # Mock embeddings
        mock_get_embedding.return_value = [0.1, 0.2, 0.3]
        
        # Set embeddings for entries
        self.entry1.embedding = [0.1, 0.2, 0.3]  # High similarity
        self.entry1.save()
        
        self.entry2.embedding = [0.9, 0.8, 0.7]  # Low similarity
        self.entry2.save()
        
        self.entry3.embedding = [0.5, 0.5, 0.5]  # Medium similarity
        self.entry3.save()
        
        # Test query
        query = "What are your business hours?"
        best_entry, score = find_best_match(self.assistant, query, threshold=0.6)
        
        self.assertEqual(best_entry, self.entry1)
        self.assertGreater(score, 0.6)
        
    @patch('assistants.semantic_search.get_embedding')
    def test_find_best_match_no_embeddings(self, mock_get_embedding):
        """Test finding best match when entries don't have embeddings"""
        # Mock embedding generation
        mock_get_embedding.return_value = [0.1, 0.2, 0.3]
        
        # Test query
        query = "What are your business hours?"
        best_entry, score = find_best_match(self.assistant, query, threshold=0.6)
        
        # Should generate embeddings and find a match
        self.assertIsNotNone(best_entry)
        self.assertGreater(score, 0)
        
    @patch('assistants.semantic_search.get_embedding')
    def test_find_best_match_below_threshold(self, mock_get_embedding):
        """Test finding best match when similarity is below threshold"""
        # Mock embeddings with low similarity
        mock_get_embedding.return_value = [0.9, 0.8, 0.7]  # Very different from entries
        
        # Set embeddings for entries
        self.entry1.embedding = [0.1, 0.2, 0.3]
        self.entry1.save()
        
        # Test query
        query = "What are your business hours?"
        best_entry, score = find_best_match(self.assistant, query, threshold=0.8)
        
        # Should return None when below threshold
        self.assertIsNone(best_entry)
        self.assertLess(score, 0.8)
        
    @patch('assistants.semantic_search.get_embedding')
    def test_find_top_matches(self, mock_get_embedding):
        """Test finding top matches"""
        # Mock embedding generation
        mock_get_embedding.return_value = [0.1, 0.2, 0.3]
        
        # Set embeddings for entries
        self.entry1.embedding = [0.1, 0.2, 0.3]  # High similarity
        self.entry1.save()
        
        self.entry2.embedding = [0.9, 0.8, 0.7]  # Low similarity
        self.entry2.save()
        
        self.entry3.embedding = [0.5, 0.5, 0.5]  # Medium similarity
        self.entry3.save()
        
        # Test query
        query = "What are your business hours?"
        top_matches = find_top_matches(self.assistant, query, top_k=2)
        
        self.assertEqual(len(top_matches), 2)
        # Should be sorted by similarity (highest first)
        self.assertEqual(top_matches[0][0], self.entry1)
        self.assertGreater(top_matches[0][1], top_matches[1][1])
        
    @patch('assistants.semantic_search.get_embedding')
    def test_find_top_matches_from_entries(self, mock_get_embedding):
        """Test finding top matches from provided entries"""
        # Mock embedding generation
        mock_get_embedding.return_value = [0.1, 0.2, 0.3]
        
        # Set embeddings for entries
        self.entry1.embedding = [0.1, 0.2, 0.3]  # High similarity
        self.entry1.save()
        
        self.entry2.embedding = [0.9, 0.8, 0.7]  # Low similarity
        self.entry2.save()
        
        self.entry3.embedding = [0.5, 0.5, 0.5]  # Medium similarity
        self.entry3.save()
        
        # Get entries
        entries = KnowledgeBaseEntry.objects.filter(assistant=self.assistant)
        
        # Test query
        query = "What are your business hours?"
        top_matches = find_top_matches_from_entries(entries, query, top_k=2)
        
        self.assertEqual(len(top_matches), 2)
        # Should be sorted by similarity (highest first)
        self.assertEqual(top_matches[0][0], self.entry1)
        self.assertGreater(top_matches[0][1], top_matches[1][1])
        
    def test_find_best_match_empty_knowledge_base(self):
        """Test finding best match with empty knowledge base"""
        # Create assistant with no knowledge base entries
        empty_assistant = Assistant.objects.create(
            user=self.user,
            name="Empty Assistant",
            tag_name="empty_assistant",
            platform="whatsapp"
        )
        
        query = "What are your business hours?"
        best_entry, score = find_best_match(empty_assistant, query, threshold=0.6)
        
        self.assertIsNone(best_entry)
        self.assertEqual(score, 0)
        
    def test_find_top_matches_empty_knowledge_base(self):
        """Test finding top matches with empty knowledge base"""
        # Create assistant with no knowledge base entries
        empty_assistant = Assistant.objects.create(
            user=self.user,
            name="Empty Assistant",
            tag_name="empty_assistant",
            platform="whatsapp"
        )
        
        query = "What are your business hours?"
        top_matches = find_top_matches(empty_assistant, query, top_k=5)
        
        self.assertEqual(len(top_matches), 0)
        
    @patch('assistants.semantic_search.get_embedding')
    def test_cosine_similarity_calculation(self, mock_get_embedding):
        """Test that cosine similarity is calculated correctly"""
        # Mock embeddings
        query_embedding = [1.0, 0.0, 0.0]
        entry_embedding = [1.0, 0.0, 0.0]  # Perfect match
        
        mock_get_embedding.return_value = query_embedding
        
        # Set embedding for entry
        self.entry1.embedding = entry_embedding
        self.entry1.save()
        
        # Test query
        query = "Test query"
        best_entry, score = find_best_match(self.assistant, query, threshold=0.6)
        
        # Should have perfect similarity (1.0)
        self.assertEqual(best_entry, self.entry1)
        self.assertAlmostEqual(score, 1.0, places=2)
        
    @patch('assistants.semantic_search.get_embedding')
    def test_embedding_generation_on_demand(self, mock_get_embedding):
        """Test that embeddings are generated when missing"""
        # Mock embedding generation
        mock_get_embedding.return_value = [0.1, 0.2, 0.3]
        
        # Ensure entries have no embeddings
        self.entry1.embedding = None
        self.entry1.save()
        
        self.entry2.embedding = None
        self.entry2.save()
        
        # Test query
        query = "What are your business hours?"
        best_entry, score = find_best_match(self.assistant, query, threshold=0.6)
        
        # Should call get_embedding for query and entries
        self.assertGreater(mock_get_embedding.call_count, 1)
        self.assertIsNotNone(best_entry)
