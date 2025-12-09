import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('talkflow')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# apps/chat/tasks.py
from celery import shared_task

@shared_task
def cleanup_old_conversations():
    """Delete conversations older than 90 days"""
    from django.utils import timezone
    from datetime import timedelta
    from apps.chat.models import Conversation
    
    threshold = timezone.now() - timedelta(days=90)
    deleted = Conversation.objects.filter(
        updated_at__lt=threshold,
        is_active=False
    ).delete()
    
    return f"Deleted {deleted[0]} conversations"