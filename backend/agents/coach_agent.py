# backend/agents/coach_agent.py
"""Coach Agent - Provides strategic tips and guidance"""

from typing import Dict, Any
from agents.base_agent import BaseAgent, AgentRole
import logging

logger = logging.getLogger(__name__)

class CoachAgent(BaseAgent):
    """Provides strategic coaching and tips for better debating"""
    
    def __init__(self, llm_service, memory_service=None):
        super().__init__(AgentRole.COACH, llm_service, memory_service)
    
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide coaching tips and strategic guidance"""
        
        context_info = self._extract_context_info(context)
        recent_user_messages = [
            msg for msg in context_info['recent_messages'] 
            if msg.get('role') == 'user'
        ]
        
        prompt = f"""
        Provide strategic coaching advice based on the current debate situation.
        
        Context:
        - Topic: {context_info['topic']}
        - User Position: {context_info['user_position']}
        - Current Round: {context_info['current_round']}
        - Phase: {context_info['phase']}
        
        User's Recent Arguments:
        {recent_user_messages[-2:] if recent_user_messages else "No recent arguments"}
        
        Task: {task}
        
        Provide 2-3 specific, actionable tips that would help improve their debating in this situation. Focus on:
        
        1. **Immediate tactical advice** - What they should do in their next argument
        2. **Strategic positioning** - How to strengthen their overall case
        3. **Debate techniques** - Specific skills they could apply
        
        Examples of good coaching tips:
        - "Try using the 'Yes, but...' technique to acknowledge their point while redirecting"
        - "Consider asking them to provide specific evidence for their claim about..."
        - "You could strengthen your argument by addressing the economic implications they raised"
        
        Keep tips practical, specific, and immediately applicable. Be encouraging and educational.
        """
        
        try:
            coaching_tips = await self._call_llm(prompt, context)
            
            return self._format_response(
                content=coaching_tips,
                reasoning="Strategic coaching advice provided",
                confidence=0.85,
                metadata={
                    "coaching_type": "strategic",
                    "round": context_info['current_round'],
                    "phase": context_info['phase']
                }
            )
            
        except Exception as e:
            logger.error(f"Coaching failed: {e}")
            return self._format_response(
                content="Here's a quick tip: Try to support your next argument with a specific example or piece of evidence. This will make your position more convincing and harder to refute.",
                reasoning="Fallback coaching tip",
                confidence=0.6
            )
    
    def _get_role_prompt(self) -> str:
        return """You are an experienced debate coach who provides strategic
        advice to help users improve their argumentation skills. You offer
        specific, actionable tips that can be immediately applied. You focus
        on technique, strategy, and skill development rather than taking
        sides on the topic being debated."""
