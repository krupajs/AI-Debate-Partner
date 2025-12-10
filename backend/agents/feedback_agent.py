# backend/agents/feedback_agent.py  
"""Feedback Agent - Evaluates debates and provides constructive feedback"""

from typing import Dict, Any
from agents.base_agent import BaseAgent, AgentRole
import logging

logger = logging.getLogger(__name__)

class FeedbackAgent(BaseAgent):
    """Provides neutral evaluation and constructive feedback on debates"""
    
    def __init__(self, llm_service, memory_service=None):
        super().__init__(AgentRole.FEEDBACK, llm_service, memory_service)
    
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide comprehensive debate evaluation"""
        
        context_info = self._extract_context_info(context)
        
        prompt = f"""
        Evaluate this debate comprehensively and provide constructive feedback.
        
        Debate Details:
        - Topic: {context_info['topic']}
        - User Position: {context_info['user_position']}
        - Total Rounds: {context_info['current_round']}
        - Messages Exchanged: {len(context_info['recent_messages'])}
        
        Recent Conversation:
        {context_info['recent_messages']}
        
        Provide evaluation covering:
        
        1. **Argument Quality Assessment**
           - Strength of user's main arguments
           - Use of evidence and examples
           - Logical consistency
           - Addressing of counter-arguments
        
        2. **Debate Skills Demonstrated**
           - Structure and organization
           - Rhetorical effectiveness  
           - Response to challenges
           - Overall persuasiveness
        
        3. **Areas for Improvement**
           - Specific weaknesses identified
           - Missed opportunities
           - Suggestions for stronger arguments
        
        4. **Strengths to Build On**
           - What the user did well
           - Effective techniques used
           - Natural debate skills shown
        
        5. **Overall Performance**
           - Brief summary of debate performance
           - Encouragement and next steps
        
        Keep feedback constructive, specific, and encouraging. Format as a comprehensive evaluation.
        """
        
        try:
            evaluation = await self._call_llm(prompt, context)
            
            return self._format_response(
                content=evaluation,
                reasoning="Comprehensive debate evaluation completed",
                confidence=0.9,
                metadata={
                    "evaluation_type": "comprehensive",
                    "rounds_evaluated": context_info['current_round'],
                    "total_exchanges": len(context_info['recent_messages'])
                }
            )
            
        except Exception as e:
            logger.error(f"Feedback generation failed: {e}")
            return self._format_response(
                content=f"Thank you for an engaging debate on {context_info['topic']}! You demonstrated good critical thinking skills and presented your arguments clearly. Consider strengthening your points with more specific evidence in future debates.",
                reasoning="Fallback feedback due to generation error",
                confidence=0.6
            )
    
    def _get_role_prompt(self) -> str:
        return """You are a neutral debate evaluator and coach. You provide
        comprehensive, constructive feedback that helps users improve their
        argumentation skills. You are encouraging but honest, specific in
        your observations, and focused on educational growth. You evaluate
        both content and technique while maintaining complete neutrality
        about the topic positions."""
