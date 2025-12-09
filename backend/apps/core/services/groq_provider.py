from typing import List, Dict
from django.conf import settings
from groq import Groq
import logging

from .llm_service import BaseLLMProvider

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """
    Groq API Provider Implementation
    Uses llama-3.3-70b-versatile (FREE & FAST)
    """
    
    def __init__(self):
        self.api_key = settings.LLM_CONFIG.get('GROQ_API_KEY')
        self.model = settings.LLM_CONFIG.get('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.timeout = settings.LLM_CONFIG.get('TIMEOUT', 30)
        self.client = None
        
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
    
    def is_available(self) -> bool:
        """Check if Groq is properly configured"""
        return self.client is not None and bool(self.api_key)
    
    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 2048,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict:
        """
        Generate response using Groq API
        
        Args:
            messages: Conversation history
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Dict with 'content', 'tokens_used', 'model', 'finish_reason'
        """
        if not self.is_available():
            raise RuntimeError("Groq provider is not configured. Check GROQ_API_KEY.")
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=self.timeout,
                **kwargs
            )
            
            # Extract response data
            choice = response.choices[0]
            usage = response.usage
            
            return {
                'content': choice.message.content,
                'tokens_used': usage.total_tokens if usage else 0,
                'prompt_tokens': usage.prompt_tokens if usage else 0,
                'completion_tokens': usage.completion_tokens if usage else 0,
                'model': response.model,
                'finish_reason': choice.finish_reason,
            }
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise RuntimeError(f"Failed to generate response: {str(e)}")
    
    def generate_streaming_response(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 2048,
        temperature: float = 0.7,
        **kwargs
    ):
        """
        Generate streaming response (for real-time chat)
        Yields chunks of text as they arrive
        """
        if not self.is_available():
            raise RuntimeError("Groq provider is not configured.")
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Groq streaming error: {str(e)}")
            raise RuntimeError(f"Streaming failed: {str(e)}")