from rest_framework import serializers
from .models import Conversation, ChatMessage, UserUsageStats


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'role', 'content', 'tokens_used', 
            'model_used', 'created_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    message_count = serializers.IntegerField(source='get_message_count', read_only=True)
    latest_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'created_at', 'updated_at', 
            'is_active', 'message_count', 'latest_message'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_latest_message(self, obj):
        latest = obj.messages.order_by('-created_at').first()
        if latest:
            return {
                'content': latest.content[:100],
                'role': latest.role,
                'created_at': latest.created_at
            }
        return None


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Detailed conversation with messages"""
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'created_at', 'updated_at', 
            'is_active', 'messages'
        ]


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat request"""
    message = serializers.CharField(required=True, max_length=4000)
    conversation_id = serializers.UUIDField(required=False, allow_null=True)
    stream = serializers.BooleanField(default=False, required=False)
    
    def validate_message(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat response"""
    conversation_id = serializers.UUIDField()
    message = ChatMessageSerializer()
    assistant_reply = ChatMessageSerializer()
    usage = serializers.DictField(required=False)


class UserUsageStatsSerializer(serializers.ModelSerializer):
    """Serializer for user usage statistics"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserUsageStats
        fields = [
            'username', 'total_messages', 'total_tokens', 
            'last_request_at', 'created_at'
        ]