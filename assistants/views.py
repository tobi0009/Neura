from rest_framework import generics, permissions
from .models import Assistant, KnowledgeBaseEntry
from .serializers import AssistantSerializer, KnowledgeBaseEntrySerializer
from .permissions import IsOwner
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .semantic_search import find_best_match, find_top_matches, find_top_matches_from_entries
from django.views import View
from django.conf import settings
from .gemini import ask_gemini, get_knowledge_context
from rest_framework.views import APIView

class AssistantListCreateView(generics.ListCreateAPIView):
    serializer_class = AssistantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Assistant.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AssistantDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssistantSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Assistant.objects.all()


class KnowledgeBaseEntryListCreateView(generics.ListCreateAPIView):
    serializer_class = KnowledgeBaseEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        assistant_id = self.request.query_params.get('assistant')
        return KnowledgeBaseEntry.objects.filter(assistant__user=self.request.user, assistant__id=assistant_id)

    def perform_create(self, serializer):
        assistant_id = self.request.data.get('assistant')
        assistant = Assistant.objects.get(id=assistant_id, user=self.request.user)
        serializer.save(assistant=assistant)


class KnowledgeBaseEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = KnowledgeBaseEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = KnowledgeBaseEntry.objects.all()

    def get_queryset(self):
        return KnowledgeBaseEntry.objects.filter(assistant__user=self.request.user)


class AnswerQueryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        query = request.GET.get("query")
        assistant_id = request.GET.get('assistant_id')

        if not query:
            return JsonResponse({"error": "No question provided"}, status=400)
        
        if not assistant_id:
            return JsonResponse({'message': 'Missing Assistant ID'}, status=400)
        
        try:
            assistant = Assistant.objects.get(id=assistant_id, user=request.user)
        except Assistant.DoesNotExist:
            return JsonResponse({'message': 'Invalid or Unauthorized Assistant'}, status=403)
        
        best_entry, score = find_best_match(assistant, query, threshold=0.6)

        if best_entry and score >= 0.7:
            return JsonResponse({
                "question": query,
                "answer": best_entry.content,
                "confidence": round(score, 2)
            })
        
        entries = KnowledgeBaseEntry.objects.filter(assistant=assistant, embedding__isnull=False)
        
        if entries:
            top_matches = find_top_matches_from_entries(entries, query, top_k=5)
            if top_matches:
                context_parts = [f"{entry.content}" for entry, _ in top_matches]
                context = "\n\n".join(context_parts)
            else:
                context = "There is no relevant information available."
        else:
            context = "There is no relevant information available."

        gemini_answer = ask_gemini(query, context)

        if gemini_answer:
            return JsonResponse({
                "question": query,
                "answer": gemini_answer,
                "confidence": 0.5
            })

        return JsonResponse({
            "question": query,
            "answer": "Sorry, I couldn't find an answer to that question.",
            "confidence": 0
        })
