from django.contrib import admin
from .models import Conversation, ChatMessage, UserUsageStats


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'get_message_count', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'user']
    search_fields = ['user__username', 'title', 'id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def get_message_count(self, obj):
        return obj.messages.count()
    get_message_count.short_description = 'Messages'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'role', 'short_content', 'tokens_used', 'model_used', 'created_at']
    list_filter = ['role', 'created_at', 'model_used']
    search_fields = ['content', 'conversation__id', 'conversation__user__username']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    def short_content(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    short_content.short_description = 'Content'


@admin.register(UserUsageStats)
class UserUsageStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_messages', 'total_tokens', 'last_request_at', 'created_at']
    list_filter = ['created_at', 'last_request_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']