from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Customize admin site
admin.site.site_header = "🤖 Neura AI Assistant Management"
admin.site.site_title = "Neura AI Admin Portal"
admin.site.index_title = "Welcome to Neura AI Assistant Management Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('userauth.urls')),
    path('api/assistants/', include('assistants.urls')),
    path('api/whatsapp/', include('whatsapp.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
