from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from twilio.twiml.messaging_response import MessagingResponse
from assistants.models import Assistant, KnowledgeBaseEntry
from assistants.semantic_search import find_best_match, find_top_matches_from_entries
from assistants.gemini import ask_gemini
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

class WhatsAppSetupInstructions(APIView):
    permission_classes = [AllowAny]  # Temporarily allow any for testing
    
    def get(self, request, assistant_id):
        """
        Get WhatsApp setup instructions for a specific assistant
        """
        try:
            assistant = Assistant.objects.get(id=assistant_id)
            
            instructions = {
                "assistant_name": assistant.name,
                "tag_name": assistant.tag_name,
                "whatsapp_number": "+14155238886",  # Your Twilio WhatsApp number
                "setup_steps": [
                    "1. Add our WhatsApp number (+14155238886) to your WhatsApp group",
                    "2. Send a test message in the group using this format:",
                    f"   @{assistant.tag_name}: what can you help me with?",
                    "3. The assistant will respond based on your knowledge base",
                    "4. Make sure your knowledge base has relevant information"
                ],
                "usage_examples": [
                    f"@{assistant.tag_name}: what are your business hours?",
                    f"@{assistant.tag_name}: how do I contact support?",
                    f"@{assistant.tag_name}: what services do you offer?"
                ],
                "tips": [
                    "Always use the @ symbol followed by the tag name",
                    "Use a colon (:) to separate the tag from your question",
                    "The assistant will respond based on your uploaded knowledge",
                    "Make sure your knowledge base is up to date"
                ]
            }
            
            return Response(instructions)
            
        except Assistant.DoesNotExist:
            return Response({"error": "Assistant not found"}, status=404)

class WhatsAppWebhook(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            # Twilio sends data as form-urlencoded, not JSON
            incoming_msg = request.data.get('Body', '')
            
            if not incoming_msg:
                return HttpResponse('No message received', status=400)

            if '@' in incoming_msg and ':' in incoming_msg:
                # Extract tag and question
                parts = incoming_msg.split(':', 1)
                tag = parts[0].replace('@', '').strip()
                question = parts[1].strip()

                if not tag or not question:
                    return HttpResponse('Invalid message format. Use: @tag_name: your question', status=400)

                # Find assistant by tag
                try:
                    assistant = Assistant.objects.get(tag_name=tag)
                except Assistant.DoesNotExist:
                    return HttpResponse(f'Assistant "{tag}" not found. Please check the tag name.', status=400)
                
                # Use the same logic as AnswerQueryView
                best_entry, score = find_best_match(assistant, question, threshold=0.6)

                # If confident match found (threshold 0.7)
                if best_entry and score >= 0.7:
                    response_text = best_entry.content
                else:
                    # Try Gemini with top 5 similar entries as context
                    entries = KnowledgeBaseEntry.objects.filter(assistant=assistant, embedding__isnull=False)
                    
                    if entries:
                        # Use the same entries for both operations
                        top_matches = find_top_matches_from_entries(entries, question, top_k=5)
                        
                        if top_matches:
                            context_parts = [f"{entry.content}" for entry, _ in top_matches]
                            context = "\n\n".join(context_parts)
                        else:
                            context = "There is no relevant information available."
                    else:
                        context = "There is no relevant information available."

                    gemini_answer = ask_gemini(question, context)

                    if gemini_answer:
                        response_text = gemini_answer
                    else:
                        response_text = "Sorry, I don't have an answer for that yet."

                twilio_response = MessagingResponse()
                twilio_response.message(response_text)

                return HttpResponse(str(twilio_response), content_type='application/xml')
            else:
                # If message doesn't follow @tag: question format
                return HttpResponse('Please use format: @tag_name: your question', status=400)
                
        except Exception as e:
            logger.error(f"WhatsApp webhook error: {str(e)}")
            return HttpResponse('An error occurred. Please try again.', status=500)
