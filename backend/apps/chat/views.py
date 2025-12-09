from rest_framework import status, generics, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
import logging

from .models import Conversation, ChatMessage, UserUsageStats
from .serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    ConversationSerializer,
    ConversationDetailSerializer,
    ChatMessageSerializer,
    UserUsageStatsSerializer
)
from apps.core.services.llm_service import LLMService
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpResponse

logger = logging.getLogger(__name__)

@method_decorator(ratelimit(key='user', rate='10/m', method='POST'), name='post')
class ChatView(views.APIView):
    """
    Main chat endpoint - Send message and get AI response
    POST /chat/
    
    Request body:
    {
        "message": "Your message here",
        "conversation_id": "uuid" (optional, creates new if not provided)
    }
    """
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        message_content = serializer.validated_data['message']
        conversation_id = serializer.validated_data.get('conversation_id')
        
        try:
            # Get or create conversation
            if conversation_id:
                conversation = Conversation.objects.select_for_update().get(
                    id=conversation_id,
                    user=user
                )
            else:
                conversation = Conversation.objects.create(user=user)
            
            # Load conversation history (limited for performance)
            history_messages = conversation.messages.order_by('created_at')[:settings.MAX_CHAT_HISTORY]
            
            # Save user message
            user_message = ChatMessage.objects.create(
                conversation=conversation,
                role='user',
                content=message_content
            )
            
            # Prepare messages for LLM
            llm_messages = LLMService.format_conversation_for_llm(history_messages)
            llm_messages.append({'role': 'user', 'content': message_content})
            
            # Call LLM service
            llm_response = LLMService.generate_chat_response(messages=llm_messages)
            
            # Save assistant response
            assistant_message = ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=llm_response['content'],
                tokens_used=llm_response.get('tokens_used', 0),
                model_used=llm_response.get('model', 'unknown'),
                metadata={
                    'prompt_tokens': llm_response.get('prompt_tokens', 0),
                    'completion_tokens': llm_response.get('completion_tokens', 0),
                    'finish_reason': llm_response.get('finish_reason', 'unknown')
                }
            )
            
            # Update conversation timestamp and generate title if first message
            conversation.updated_at = timezone.now()
            conversation.save()
            
            if conversation.get_message_count() == 2 and not conversation.title:
                conversation.generate_title()
            
            # Update user usage stats
            usage_stats, _ = UserUsageStats.objects.get_or_create(user=user)
            usage_stats.increment_usage(tokens=llm_response.get('tokens_used', 0))
            
            # Return response
            response_data = {
                'conversation_id': str(conversation.id),
                'user_message': ChatMessageSerializer(user_message).data,
                'assistant_message': ChatMessageSerializer(assistant_message).data,
                'usage': {
                    'prompt_tokens': llm_response.get('prompt_tokens', 0),
                    'completion_tokens': llm_response.get('completion_tokens', 0),
                    'total_tokens': llm_response.get('tokens_used', 0),
                }
            }
            
            return Response({
                'success': True,
                'data': response_data
            }, status=status.HTTP_200_OK)
            
        except Conversation.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            logger.error(f"Chat error for user {user.username}: {str(e)}")
            return Response({
                'success': False,
                'error': f'Failed to generate response: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationListView(generics.ListAPIView):
    """
    List all conversations for current user
    GET /chat/conversations/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        return Conversation.objects.filter(
            user=self.request.user,
            is_active=True
        ).prefetch_related('messages')


class ConversationDetailView(generics.RetrieveDestroyAPIView):
    """
    Get conversation details with full message history
    GET /chat/conversations/<uuid>/
    DELETE /chat/conversations/<uuid>/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationDetailSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete conversation"""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({
            'success': True,
            'message': 'Conversation deleted successfully'
        }, status=status.HTTP_200_OK)


class ChatHistoryView(generics.ListAPIView):
    """
    Get chat history for a specific conversation
    GET /chat/history/?conversation_id=<uuid>
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChatMessageSerializer
    
    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation_id')
        
        if not conversation_id:
            return ChatMessage.objects.none()
        
        return ChatMessage.objects.filter(
            conversation__id=conversation_id,
            conversation__user=self.request.user
        ).order_by('created_at')


class UserStatsView(generics.RetrieveAPIView):
    """
    Get current user's usage statistics
    GET /chat/stats/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserUsageStatsSerializer
    
    def get_object(self):
        obj, _ = UserUsageStats.objects.get_or_create(user=self.request.user)
        return obj
    
from django.http import StreamingHttpResponse
import json

class ChatStreamView(views.APIView):
    """
    Streaming chat endpoint for real-time responses
    GET /chat/stream/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message_content = serializer.validated_data['message']
        conversation_id = serializer.validated_data.get('conversation_id')
        
        def event_stream():
            try:
                # Get/create conversation
                if conversation_id:
                    conversation = Conversation.objects.get(
                        id=conversation_id, user=request.user
                    )
                else:
                    conversation = Conversation.objects.create(user=request.user)
                
                # Save user message
                user_message = ChatMessage.objects.create(
                    conversation=conversation,
                    role='user',
                    content=message_content
                )
                
                # Prepare messages
                history = conversation.messages.order_by('created_at')[:50]
                llm_messages = LLMService.format_conversation_for_llm(history)
                llm_messages.append({'role': 'user', 'content': message_content})
                
                # Stream response
                from apps.core.services.groq_provider import GroqProvider
                provider = GroqProvider()
                
                full_response = ""
                for chunk in provider.generate_streaming_response(llm_messages):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Save complete response
                assistant_message = ChatMessage.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=full_response,
                    model_used='llama-3.3-70b-versatile'
                )
                
                yield f"data: {json.dumps({'done': True, 'message_id': str(assistant_message.id)})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
            }
        )
    
class ConversationSearchView(generics.ListAPIView):
    """Search conversations by title or content"""
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Conversation.objects.filter(
            user=self.request.user,
            is_active=True
        ).filter(
            Q(title__icontains=query) |
            Q(messages__content__icontains=query)
        ).distinct()
    
class ConversationExportView(views.APIView):
    """Export conversation as JSON/Markdown"""
    
    def get(self, request, id):
        conversation = get_object_or_404(
            Conversation, id=id, user=request.user
        )
        
        format_type = request.query_params.get('format', 'json')
        
        if format_type == 'markdown':
            content = f"# {conversation.title}\n\n"
            for msg in conversation.messages.all():
                content += f"**{msg.role.title()}:** {msg.content}\n\n"
            
            return HttpResponse(content, content_type='text/markdown')
        
        # JSON export
        data = ConversationDetailSerializer(conversation).data
        return Response(data)