from django.urls import path
from .views import AssistantListCreateView, AssistantDetailView, KnowledgeBaseEntryListCreateView, KnowledgeBaseEntryDetailView, AnswerQueryView

urlpatterns = [
    path('', AssistantListCreateView.as_view(), name='assistant-list-create'),
    path('<int:pk>/', AssistantDetailView.as_view(), name='assistant-detail'),

    # Knowledge Base Routes
    path('knowledge/', KnowledgeBaseEntryListCreateView.as_view(), name='knowledge-list-create'),
    path('knowledge/<int:pk>/', KnowledgeBaseEntryDetailView.as_view(), name='knowledge-detail'),

    path("answer/", AnswerQueryView.as_view(), name="answer_query"),
]
