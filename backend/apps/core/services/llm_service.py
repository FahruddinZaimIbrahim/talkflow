from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from django.conf import settings


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers
    This allows easy switching between different LLM APIs
    """
    
    @abstractmethod
    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> Dict:
        """
        Generate response from LLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Dict containing 'content', 'tokens_used', 'model' etc.
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is properly configured"""
        pass


class LLMService:
    """
    Main service class for LLM operations
    Factory pattern to select provider dynamically
    """
    
    _provider: Optional[BaseLLMProvider] = None
    
    @classmethod
    def get_provider(cls) -> BaseLLMProvider:
        """Get configured LLM provider (singleton pattern)"""
        if cls._provider is None:
            provider_name = settings.LLM_CONFIG.get('PROVIDER', 'groq')
            
            if provider_name == 'groq':
                from .groq_provider import GroqProvider
                cls._provider = GroqProvider()
            # Add more providers here
            # elif provider_name == 'deepseek':
            #     from .deepseek_provider import DeepSeekProvider
            #     cls._provider = DeepSeekProvider()
            else:
                raise ValueError(f"Unknown LLM provider: {provider_name}")
        
        return cls._provider
    
    @classmethod
    def generate_chat_response(
        cls,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict:
        """
        Generate chat response using configured provider
        
        Args:
            messages: Conversation history
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Dict with response data
        """
        provider = cls.get_provider()
        
        if not provider.is_available():
            raise RuntimeError("LLM provider is not properly configured")
        
        # Use defaults from settings if not provided
        if max_tokens is None:
            max_tokens = settings.LLM_CONFIG.get('MAX_TOKENS', 2048)
        
        if temperature is None:
            temperature = settings.LLM_CONFIG.get('TEMPERATURE', 0.7)
        
        return provider.generate_response(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
    
    @classmethod
    def format_conversation_for_llm(cls, conversation_messages) -> List[Dict[str, str]]:
        """
        Format Django ChatMessage queryset to LLM API format
        
        Args:
            conversation_messages: QuerySet of ChatMessage objects
        
        Returns:
            List of message dicts for LLM API
        """
        return [
            {
                'role': msg.role,
                'content': msg.content
            }
            for msg in conversation_messages
        ]