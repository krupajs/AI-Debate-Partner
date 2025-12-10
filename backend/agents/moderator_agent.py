# backend/agents/moderator_agent.py
"""Moderator Agent - Maintains neutrality and manages debate flow"""

from typing import Dict, Any
from agents.base_agent import BaseAgent, AgentRole
import logging

logger = logging.getLogger(__name__)

class ModeratorAgent(BaseAgent):
    """Neutral moderator that manages debate flow and announcements"""
    
    def __init__(self, llm_service, memory_service=None):
        super().__init__(AgentRole.MODERATOR, llm_service, memory_service)
    
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute moderator tasks neutrally"""
        
        context_info = self._extract_context_info(context)
        
        prompt = f"""
        You are a neutral debate moderator. Your task: {task}
        
        Current Debate Context:
        - Topic: {context_info['topic']}
        - Phase: {context_info['phase']}
        - Round: {context_info['current_round']}
        - User Position: {context_info['user_position']}
        
        Your response should be:
        1. Completely neutral and unbiased
        2. Professional and encouraging
        3. Clear about next steps or expectations
        4. Educational about debate process
        5. 50-150 words unless task requires more
        
        Recent messages for context: {context_info['recent_messages'][-2:] if context_info['recent_messages'] else []}
        """
        
        try:
            response = await self._call_llm(prompt, context)
            
            return self._format_response(
                content=response,
                reasoning="Neutral moderation response",
                confidence=0.9,
                metadata={"neutral": True, "phase": context_info['phase']}
            )
            
        except Exception as e:
            logger.error(f"Moderator execution failed: {e}")
            return self._format_response(
                content="Let's continue with our structured debate. Please share your thoughts.",
                reasoning="Fallback moderation response",
                confidence=0.5
            )
    
    def _get_role_prompt(self) -> str:
        return """You are a professional debate moderator. You maintain strict neutrality,
        ensure fair play, announce transitions between phases, and provide clear guidance
        about debate structure. You never take sides but encourage rigorous thinking
        from all participants."""
