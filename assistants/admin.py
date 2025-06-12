from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Assistant, KnowledgeBaseEntry


class KnowledgeBaseEntryInline(admin.TabularInline):
    model = KnowledgeBaseEntry
    extra = 1
    fields = ('id', 'content', 'created_at')
    readonly_fields = ('id', 'created_at',)
    ordering = ('-created_at',)


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'platform', 'group_id', 'created_at', 'knowledge_entries_count', 'avatar_preview')
    list_filter = ('platform', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'avatar_preview')
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'user')
        }),
        ('Platform Configuration', {
            'fields': ('platform', 'group_id')
        }),
        ('Media', {
            'fields': ('avatar', 'avatar_preview'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [KnowledgeBaseEntryInline]
    
    def knowledge_entries_count(self, obj):
        count = obj.knowledge_entries.count()
        url = reverse('admin:assistants_knowledgebaseentry_changelist') + f'?assistant__id__exact={obj.id}'
        return format_html('<a href="{}">{} entries</a>', url, count)
    knowledge_entries_count.short_description = 'Knowledge Entries'
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px;" />',
                obj.avatar.url
            )
        return "No avatar"
    avatar_preview.short_description = 'Avatar Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('knowledge_entries')


@admin.register(KnowledgeBaseEntry)
class KnowledgeBaseEntryAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'content_preview', 'created_at', 'updated_at')
    list_filter = ('assistant__platform', 'created_at', 'updated_at', 'assistant')
    search_fields = ('content', 'assistant__name', 'assistant__user__email')
    readonly_fields = ('created_at', 'updated_at', 'embedding_info')
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Content', {
            'fields': ('assistant', 'content')
        }),
        ('Technical Details', {
            'fields': ('embedding_info',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def embedding_info(self, obj):
        if obj.embedding:
            return format_html(
                '<div style="background: #f0f0f0; padding: 10px; border-radius: 5px;">'
                '<strong>Embedding Vector:</strong><br>'
                '<small>Length: {} dimensions</small><br>'
                '<small>First 5 values: {}</small>'
                '</div>',
                len(obj.embedding),
                obj.embedding[:5] if obj.embedding else 'None'
            )
        return "No embedding generated yet"
    embedding_info.short_description = 'Embedding Information'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('assistant', 'assistant__user')


# Customize the admin site
admin.site.site_header = "🤖 Neura AI Assistant Management"
admin.site.site_title = "Neura AI Admin"
admin.site.index_title = "Welcome to Neura AI Assistant Management Portal"

# Add some helpful admin actions
@admin.action(description="Mark selected assistants as active")
def make_active(modeladmin, request, queryset):
    queryset.update(updated_at=timezone.now())

@admin.action(description="Generate embeddings for selected knowledge entries")
def generate_embeddings(modeladmin, request, queryset):
    # This would integrate with your embedding generation logic
    count = queryset.count()
    modeladmin.message_user(request, f"Embedding generation initiated for {count} entries.")

# Add the actions to the admin classes
AssistantAdmin.actions = [make_active]
KnowledgeBaseEntryAdmin.actions = [generate_embeddings] 