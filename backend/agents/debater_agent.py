"""Debater Agents - Generate arguments for both sides of debates"""

from typing import Dict, Any
from agents.base_agent import BaseAgent, AgentRole
import logging

logger = logging.getLogger(__name__)

class DebaterForAgent(BaseAgent):
    """Agent that argues FOR the user's position (supportive debating)"""
    
    def __init__(self, llm_service, memory_service=None):
        super().__init__(AgentRole.DEBATER_FOR, llm_service, memory_service)
    
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate arguments supporting the user's position"""
        
        context_info = self._extract_context_info(context)
        
        prompt = f"""
        Generate a strong argument SUPPORTING the user's position.
        
        Topic: {context_info['topic']}
        User's Position: {context_info['user_position']}
        Current Round: {context_info['current_round']}
        
        Task: {task}
        
        Your argument should:
        1. Strongly support the user's position
        2. Provide evidence or examples
        3. Use persuasive language
        4. Address potential counterarguments
        5. Be engaging and educational
        6. Be 100-300 words
        
        Recent context: {context_info['recent_messages'][-3:] if context_info['recent_messages'] else []}
        """
        
        try:
            response = await self._call_llm(prompt, context)
            
            return self._format_response(
                content=response,
                reasoning="Generated supportive argument for user's position",
                confidence=0.8,
                metadata={"position": "for", "round": context_info['current_round']}
            )
            
        except Exception as e:
            logger.error(f"DebaterFor execution failed: {e}")
            return self._format_response(
                content="I support your position on this topic. Let me gather my thoughts for a stronger argument.",
                reasoning="Fallback response due to error",
                confidence=0.3
            )
    
    def _get_role_prompt(self) -> str:
        return """You are a skilled debater who SUPPORTS the user's position. 
        Your role is to strengthen their arguments, provide additional evidence, 
        and help them build a compelling case. You are collaborative and educational, 
        helping the user see the strongest points of their chosen side."""

class DebaterAgainstAgent(BaseAgent):
    """Agent that argues AGAINST the user's position (challenging debating)"""
    
    def __init__(self, llm_service, memory_service=None):
        super().__init__(AgentRole.DEBATER_AGAINST, llm_service, memory_service)
    
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate arguments opposing the user's position"""
        
        context_info = self._extract_context_info(context)
        
        # Determine what we're arguing against
        if context_info['user_position'] == 'for':
            our_position = 'against'
            opposing_position = 'for'
        else:
            our_position = 'for' 
            opposing_position = 'against'
        
        prompt = f"""
        Generate a strong argument OPPOSING the user's position.
        
        Topic: {context_info['topic']}
        User's Position: {context_info['user_position']} 
        Your Position: {our_position}
        Current Round: {context_info['current_round']}
        
        Task: {task}
        
        Your argument should:
        1. Respectfully challenge the user's position
        2. Present strong counter-evidence
        3. Identify logical weaknesses
        4. Use compelling examples
        5. Maintain a challenging but fair tone
        6. Be educational and thought-provoking
        7. Be 100-300 words
        
        Recent context: {context_info['recent_messages'][-3:] if context_info['recent_messages'] else []}
        
        Remember: Challenge ideas, not the person. Be rigorous but respectful.
        """
        
        try:
            response = await self._call_llm(prompt, context)
            
            return self._format_response(
                content=response,
                reasoning=f"Generated challenging argument opposing user's {opposing_position} position",
                confidence=0.85,
                metadata={
                    "position": our_position, 
                    "opposing": opposing_position,
                    "round": context_info['current_round']
                }
            )
            
        except Exception as e:
            logger.error(f"DebaterAgainst execution failed: {e}")
            return self._format_response(
                content=f"I understand your position, but let me present an alternative perspective on {context_info['topic']}.",
                reasoning="Fallback response due to error",
                confidence=0.3
            )
    
    def _get_role_prompt(self) -> str:
        return """You are a skilled debater who provides OPPOSITION to the user's position.
        Your role is to challenge their arguments constructively, present strong counter-evidence,
        and help them strengthen their reasoning by facing rigorous opposition. You are
        intellectually honest, respectful, and focused on helping them become a better debater
        through challenging discourse."""