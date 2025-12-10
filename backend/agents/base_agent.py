"""Base agent class for all debate agents"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AgentRole(str, Enum):
    CONTROLLER = "controller"
    MODERATOR = "moderator"
    TOPIC_GENERATOR = "topic_generator"
    DEBATER_FOR = "debater_for"
    DEBATER_AGAINST = "debater_against"
    MEMORY = "memory"
    FEEDBACK = "feedback"
    COACH = "coach"

class BaseAgent(ABC):
    """Abstract base class for all debate agents"""
    
    def __init__(self, role: AgentRole, llm_service=None, memory_service=None):
        self.role = role
        self.llm_service = llm_service
        self.memory_service = memory_service
        self.agent_id = f"{role.value}_{id(self)}"
        
    @abstractmethod
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's primary function
        
        Args:
            task: Specific task description
            context: Current debate context and state
            
        Returns:
            Dict containing the agent's response and metadata
        """
        pass
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        return self._get_role_prompt()
    
    @abstractmethod
    def _get_role_prompt(self) -> str:
        """Get the role-specific system prompt"""
        pass
    
    async def _call_llm(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Helper method to call LLM service"""
        if not self.llm_service:
            raise ValueError("LLM service not configured for agent")
            
        system_prompt = self.get_system_prompt()
        full_prompt = f"{system_prompt}\n\nContext: {context}\n\nTask: {prompt}"
        
        try:
            response = await self.llm_service.generate_response(full_prompt)
            return response
        except Exception as e:
            logger.error(f"LLM call failed for agent {self.agent_id}: {e}")
            raise
    
    def _extract_context_info(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant information from context"""
        return {
            "topic": context.get("topic", ""),
            "user_position": context.get("user_position", ""),
            "ai_position": context.get("ai_position", ""),
            "current_round": context.get("current_round", 0),
            "phase": context.get("phase", ""),
            "recent_messages": context.get("recent_messages", [])
        }
    
    def _format_response(self, content: str, reasoning: str = "", 
                        confidence: float = 0.8, metadata: Dict = None) -> Dict[str, Any]:
        """Format agent response in standard format"""
        return {
            "agent_name": self.role.value,
            "content": content,
            "reasoning": reasoning,
            "confidence": confidence,
            "metadata": metadata or {}
        }