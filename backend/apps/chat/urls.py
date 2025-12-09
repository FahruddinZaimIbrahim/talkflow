from django.urls import path
from .views import (
    ChatView,
    ConversationListView,
    ConversationDetailView,
    ChatHistoryView,
    UserStatsView,
    ChatStreamView,
)

app_name = 'chat'

urlpatterns = [
    # Main chat endpoint
    path('', ChatView.as_view(), name='chat'),
    
    # Conversation management
    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('conversations/<uuid:id>/', ConversationDetailView.as_view(), name='conversation_detail'),
    
    # History and stats
    path('history/', ChatHistoryView.as_view(), name='chat_history'),
    path('stats/', UserStatsView.as_view(), name='user_stats'),
    path('stream/', ChatStreamView.as_view(), name='chat_stream'),
]