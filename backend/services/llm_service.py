"""LLM Service for integrating with Google Gemini"""

import google.generativeai as genai
from typing import Optional, Dict, Any
import logging
from utils.config import Config

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with LLM providers"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self._configure_genai()
        self.model = genai.GenerativeModel(Config.DEFAULT_MODEL)
        
    def _configure_genai(self):
        """Configure Google Generative AI"""
        genai.configure(api_key=self.api_key)
        
    async def generate_response(self, prompt: str, 
                              temperature: float = None,
                              max_tokens: int = None) -> str:
        """Generate response from LLM"""
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature or Config.TEMPERATURE,
            max_output_tokens=max_tokens or Config.MAX_TOKENS,
        )
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            if response.candidates:
                return response.candidates[0].content.parts[0].text
            else:
                logger.warning("No candidates in LLM response")
                return "I'm having trouble generating a response right now. Please try again."
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    async def generate_structured_response(self, prompt: str, 
                                         schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured response based on schema"""
        
        structured_prompt = f"""
        {prompt}
        
        Please respond in the following JSON format:
        {schema}
        
        Ensure your response is valid JSON that matches the schema exactly.
        """
        
        try:
            response = await self.generate_response(structured_prompt)
            # Try to parse as JSON
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse structured response as JSON")
            # Return fallback structure
            return {"content": response, "error": "Failed to parse as structured response"}
    
    def validate_api_key(self) -> bool:
        """Validate that API key is working"""
        try:
            # Simple test generation
            test_prompt = "Say 'API key is working' if you can respond."
            response = self.model.generate_content(test_prompt)
            return bool(response.candidates)
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False