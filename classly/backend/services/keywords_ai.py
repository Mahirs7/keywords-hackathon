"""
Keywords AI Service
Handles integration with Keywords AI Gateway for LLM calls
"""

import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class KeywordsAIService:
    """Service for interacting with Keywords AI Gateway"""
    
    def __init__(self):
        self.api_key = os.getenv('KEYWORDS_AI_API_KEY')
        # Keywords AI Gateway URL
        # According to docs: https://api.keywordsai.co/api/chat/completions
        # For LangChain, we need the base URL: https://api.keywordsai.co/api
        default_gateway = os.getenv('KEYWORDS_AI_GATEWAY_URL', 'https://api.keywordsai.co/api')
        
        # Clean up URL - remove /chat/completions if present
        gateway = default_gateway.rstrip('/')
        if gateway.endswith('/chat/completions'):
            gateway = gateway.replace('/chat/completions', '')
        if gateway.endswith('/api'):
            # Keep as is - this is correct
            pass
        elif gateway.endswith('/v1'):
            # Convert /v1 to /api
            gateway = gateway.replace('/v1', '/api')
        elif not gateway.endswith('/api'):
            # Add /api if not present
            gateway = f"{gateway}/api"
        
        self.gateway_url = gateway
        self.base_url = f"{self.gateway_url}/chat/completions"
        
    def is_configured(self) -> bool:
        """Check if Keywords AI is properly configured"""
        return self.api_key is not None and self.api_key != ""
    
    def chat_completion(
        self,
        messages: list,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a chat completion request through Keywords AI Gateway
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (default: gpt-4o-mini)
            temperature: Sampling temperature
            **kwargs: Additional parameters for the API call
            
        Returns:
            Response from Keywords AI Gateway
        """
        if not self.is_configured():
            raise ValueError("Keywords AI API key not configured. Set KEYWORDS_AI_API_KEY in .env")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Keywords AI API error: {str(e)}")
    
    def get_llm_client(self):
        """
        Get an OpenAI-compatible client configured for Keywords AI Gateway
        This can be used with LangChain
        
        Note: You must add your OpenAI API key in Keywords AI dashboard
        for the gateway to work. Keywords AI uses your credentials to call LLMs.
        """
        if not self.is_configured():
            raise ValueError("Keywords AI API key not configured")
        
        try:
            from openai import OpenAI
            
            # Keywords AI Gateway endpoint: https://api.keywordsai.co/api/chat/completions
            # For LangChain, we use base_url: https://api.keywordsai.co/api
            # LangChain will append /chat/completions automatically
            gateway_base = self.gateway_url.rstrip('/')
            
            client = OpenAI(
                api_key=self.api_key,  # Keywords AI API key
                base_url=gateway_base   # https://api.keywordsai.co/api
            )
            return client
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")

# Singleton instance
keywords_ai_service = KeywordsAIService()

