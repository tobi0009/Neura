from django.conf import settings
import google.generativeai as genai  
from .models import KnowledgeBaseEntry   

# Configure the Gemini SDK once when this module is imported
genai.configure(api_key=settings.GEMINI_API_KEY)

_model = None

#Lazy loading for gemini 
def get_gemini_model():
    global _model
    if _model is None:
        _model = genai.GenerativeModel("gemini-2.0-flash")
    return _model

MAX_CONTEXT_LENGTH = 3000  # You can tweak this if needed

def get_knowledge_context(assistant):
    """
    Combine all entries into a context block for Gemini.
    """
    entries = KnowledgeBaseEntry.objects.filter(assistant=assistant, embedding__isnull=False)
    context_blocks = []

    for entry in entries:
        block = f"- {entry.content}"
        context_blocks.append(block)

    # return "\n".join(context_blocks)
    full_context = "\n".join(context_blocks)
    return full_context[:MAX_CONTEXT_LENGTH]





def ask_gemini(query: str, context: str) -> str:
    """
    Send a prompt to Gemini and return the generated response text.
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
        # Extract the text content from the response object
        return response.text.strip()

    except Exception as e:
        # Log error or handle gracefully
        print(f"Gemini API error: {e}")
        return None
