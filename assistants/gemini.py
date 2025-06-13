from django.conf import settings
import google.generativeai as genai  
from .models import KnowledgeBaseEntry   

genai.configure(api_key=settings.GEMINI_API_KEY)

_model = None

def get_gemini_model():
    """
    Lazily load and cache the Gemini model for efficiency.
    """
    global _model
    if _model is None:
        _model = genai.GenerativeModel("gemini-2.0-flash")
    return _model

MAX_CONTEXT_LENGTH = 3000

def get_knowledge_context(assistant):
    """
    Build a context string from all knowledge base entries for Gemini.
    """
    entries = KnowledgeBaseEntry.objects.filter(assistant=assistant, embedding__isnull=False)
    context_blocks = []
    for entry in entries:
        block = f"- {entry.content}"
        context_blocks.append(block)
    full_context = "\n".join(context_blocks)
    return full_context[:MAX_CONTEXT_LENGTH]

def ask_gemini(query: str, context: str) -> str:
    """
    Query Gemini with a prompt and context, returning the answer as text.
    """
    prompt = f"""
    You are a smart assistant. Only answer based on the information in the context below.
    If the answer is not found in the context, reply: "I don't have that information."

    ### CONTEXT ###
    {context}

    ### QUESTION ###
    {query}
    """.strip()

    try:
        model = get_gemini_model()
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None
