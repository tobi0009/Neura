from django.urls import path
from .views import WhatsAppWebhook, WhatsAppSetupInstructions

urlpatterns = [
    path('webhook/', WhatsAppWebhook.as_view(), name='whatsapp-webhook'),
    path('setup/<int:assistant_id>/', WhatsAppSetupInstructions.as_view(), name='whatsapp-setup'),
]
