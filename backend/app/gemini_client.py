"""
Gemini AI client configuration for LangGraph agents.
Provides structured output generation with safety settings.
"""

import os
import re
import json
from typing import Dict, Any, Optional, Type, TypeVar
from pydantic import BaseModel

from google import genai
from google.genai import types
from google.genai.types import HarmCategory, HarmBlockThreshold

from app.config import settings

T = TypeVar('T', bound=BaseModel)


class GeminiClient:
    """Minimal Gemini client with structured output support."""
    
    def __init__(self):
        """Initialize Gemini client with API key and safety settings."""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Initialize client with API key
        self.client = genai.Client(api_key=settings.google_api_key)
        
        # Configure safety settings for production use
        self.safety_settings = [
            types.SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            ),
            types.SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            ),
            types.SafetySetting(
                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            ),
            types.SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            )
        ]
    
    def _clean_json_response(self, text: str) -> str:
        """Extract JSON from markdown-wrapped response."""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*$', '', text)
        text = text.strip()
        
        # Try to parse as JSON to validate
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            # If still invalid, try to extract JSON object
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return match.group(0)
            raise ValueError("No valid JSON found in response")
    
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        temperature: float = 0.1
    ) -> T:
        """Generate structured response using Pydantic schema."""
        try:
            # Configure generation parameters
            config = types.GenerateContentConfig(
                temperature=temperature,
                safety_settings=self.safety_settings
            )
            
            # Generate response
            response = await self.client.aio.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=config
            )
            
            if not response.text:
                raise RuntimeError("No response text generated")
            
            # Clean JSON response
            cleaned_text = self._clean_json_response(response.text)
            
            # Parse and validate response
            return response_schema.model_validate_json(cleaned_text)
            
        except Exception as e:
            raise RuntimeError(f"Gemini generation failed: {str(e)}")
    
    async def generate_text(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate simple text response."""
        try:
            config = types.GenerateContentConfig(
                temperature=temperature,
                safety_settings=self.safety_settings
            )
            
            response = await self.client.aio.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=config
            )
            
            if not response.text:
                raise RuntimeError("No response text generated")
                
            return response.text
            
        except Exception as e:
            raise RuntimeError(f"Gemini text generation failed: {str(e)}")


# Global client instance
gemini_client = GeminiClient() 