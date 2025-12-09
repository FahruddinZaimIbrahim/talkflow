from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Conversation(models.Model):
    """
    Represents a chat conversation/thread
    Each user can have multiple conversations
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title or self.id}"
    
    def get_message_count(self):
        return self.messages.count()
    
    def generate_title(self):
        """Auto-generate title from first message"""
        first_message = self.messages.filter(role='user').first()
        if first_message:
            self.title = first_message.content[:50]
            self.save(update_fields=['title'])


class ChatMessage(models.Model):
    """
    Stores individual chat messages
    Role can be 'user' or 'assistant'
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    tokens_used = models.IntegerField(null=True, blank=True)
    model_used = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['conversation', 'role']),
        ]
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class UserUsageStats(models.Model):
    """
    Track user API usage for rate limiting and analytics
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usage_stats')
    total_messages = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    last_request_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'User usage stats'
    
    def __str__(self):
        return f"{self.user.username} - {self.total_messages} messages"
    
    def increment_usage(self, tokens=0):
        self.total_messages += 1
        self.total_tokens += tokens
        self.last_request_at = timezone.now()
        self.save()