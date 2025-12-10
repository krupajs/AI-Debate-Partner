"""Core debate service that orchestrates all agents"""

from typing import Dict, Optional
import asyncio
import logging
from datetime import datetime

from models.debate_models import (
    DebateState, DebateResponse, DebatePhase, MessageRole, 
    DebateMessage, TopicRequest, AgentResponse
)
from agents.base_agent import AgentRole
from agents.controller_agent import ControllerAgent
from agents.moderator_agent import ModeratorAgent
from agents.topic_generator import TopicGeneratorAgent
from agents.debater_agent import DebaterForAgent, DebaterAgainstAgent
from agents.memory_agent import MemoryAgent
from agents.feedback_agent import FeedbackAgent
from agents.coach_agent import CoachAgent
from services.llm_service import LLMService

logger = logging.getLogger(__name__)

class DebateService:
    """Core service that manages the entire debate system"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.agents: Dict[AgentRole, any] = {}
        self.controller_agent: Optional[ControllerAgent] = None
    
    async def initialize(self):
        """Initialize all agents"""
        try:
            # Initialize memory service (simplified for now)
            memory_service = None  # TODO: Implement ChromaDB integration
            
            # Create all agents
            self.agents = {
                AgentRole.MODERATOR: ModeratorAgent(self.llm_service, memory_service),
                AgentRole.TOPIC_GENERATOR: TopicGeneratorAgent(self.llm_service, memory_service),
                AgentRole.DEBATER_FOR: DebaterForAgent(self.llm_service, memory_service),
                AgentRole.DEBATER_AGAINST: DebaterAgainstAgent(self.llm_service, memory_service),
                AgentRole.MEMORY: MemoryAgent(self.llm_service, memory_service),
                AgentRole.FEEDBACK: FeedbackAgent(self.llm_service, memory_service),
                AgentRole.COACH: CoachAgent(self.llm_service, memory_service)
            }
            
            # Create controller agent with access to all other agents
            self.controller_agent = ControllerAgent(
                self.llm_service, 
                memory_service, 
                self.agents
            )
            
            logger.info("All agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    async def start_debate(self, session_id: str, topic_request: Optional[TopicRequest]) -> DebateResponse:
        """Start a new debate session"""
        try:
            # Create new debate state
            debate_state = DebateState(
                session_id=session_id,
                phase=DebatePhase.SETUP
            )
            
            # Generate topic if needed
            if topic_request and topic_request.custom_topic:
                debate_state.topic = topic_request.custom_topic
            else:
                # Use controller to generate topic
                context = self._build_context(debate_state)
                if topic_request:
                    context["topic_request"] = topic_request.dict()
                
                response = await self.controller_agent.execute("Generate a debate topic", context)
                debate_state.topic = response.get("content", "Should AI be regulated more strictly?")
            
            # Add system message
            system_msg = DebateMessage(
                role=MessageRole.SYSTEM,
                content=f"Debate topic: {debate_state.topic}",
                agent_used="topic_generator"
            )
            debate_state.messages.append(system_msg)
            
            # Get moderator introduction
            context = self._build_context(debate_state)
            moderator_response = await self.agents[AgentRole.MODERATOR].execute(
                "Introduce the debate and ask user to choose their position", 
                context
            )
            
            # Add moderator message
            moderator_msg = DebateMessage(
                role=MessageRole.AI,
                content=moderator_response.get("content", "Welcome to the debate!"),
                agent_used="moderator"
            )
            debate_state.messages.append(moderator_msg)
            debate_state.updated_at = datetime.now()
            
            return DebateResponse(
                success=True,
                session_id=session_id,
                current_state=debate_state,
                ai_response=AgentResponse(**moderator_response)
            )
            
        except Exception as e:
            logger.error(f"Failed to start debate: {e}")
            return DebateResponse(
                success=False,
                session_id=session_id,
                current_state=DebateState(session_id=session_id),
                error=str(e)
            )
    
    async def continue_debate(self, session_id: str, user_message: str, 
                            current_state: DebateState) -> DebateResponse:
        """Continue an ongoing debate"""
        try:
            # Add user message to state
            user_msg = DebateMessage(
                role=MessageRole.USER,
                content=user_message
            )
            current_state.messages.append(user_msg)
            
            # Update user position if not set and we can infer it
            if not current_state.user_position and current_state.phase == DebatePhase.SETUP:
                if any(word in user_message.lower() for word in ["support", "agree", "for", "yes"]):
                    current_state.user_position = "for"
                    current_state.ai_position = "against"
                elif any(word in user_message.lower() for word in ["oppose", "disagree", "against", "no"]):
                    current_state.user_position = "against"
                    current_state.ai_position = "for"
                
                if current_state.user_position:
                    current_state.phase = DebatePhase.OPENING
                    current_state.current_round = 1
            
            # Build context for controller
            context = self._build_context(current_state)
            context["user_message"] = user_message
            
            # Let controller decide what to do
            controller_response = await self.controller_agent.execute(user_message, context)
            
            # Add AI response to messages
            ai_msg = DebateMessage(
                role=MessageRole.AI,
                content=controller_response.get("content", "I need to think about that..."),
                agent_used=controller_response.get("agent_name", "controller"),
                metadata=controller_response.get("metadata", {})
            )
            current_state.messages.append(ai_msg)
            current_state.updated_at = datetime.now()
            
            # Update round if we're in active debate
            if current_state.phase in [DebatePhase.OPENING, DebatePhase.REBUTTAL]:
                if len([msg for msg in current_state.messages if msg.role == MessageRole.USER]) > current_state.current_round:
                    current_state.current_round += 1
            
            return DebateResponse(
                success=True,
                session_id=session_id,
                current_state=current_state,
                ai_response=AgentResponse(**controller_response)
            )
            
        except Exception as e:
            logger.error(f"Failed to continue debate: {e}")
            return DebateResponse(
                success=False,
                session_id=session_id,
                current_state=current_state,
                error=str(e)
            )
    
    async def end_debate(self, session_id: str, current_state: DebateState) -> DebateResponse:
        """End debate and provide evaluation"""
        try:
            current_state.phase = DebatePhase.EVALUATION
            
            # Get feedback from feedback agent
            context = self._build_context(current_state)
            feedback_response = await self.agents[AgentRole.FEEDBACK].execute(
                "Evaluate the entire debate and provide comprehensive feedback",
                context
            )
            
            # Add evaluation message
            eval_msg = DebateMessage(
                role=MessageRole.AI,
                content=feedback_response.get("content", "Thank you for the engaging debate!"),
                agent_used="feedback"
            )
            current_state.messages.append(eval_msg)
            current_state.phase = DebatePhase.COMPLETE
            current_state.updated_at = datetime.now()
            
            return DebateResponse(
                success=True,
                session_id=session_id,
                current_state=current_state,
                ai_response=AgentResponse(**feedback_response)
            )
            
        except Exception as e:
            logger.error(f"Failed to end debate: {e}")
            return DebateResponse(
                success=False,
                session_id=session_id,
                current_state=current_state,
                error=str(e)
            )
    
    def _build_context(self, state: DebateState) -> Dict:
        """Build context dictionary for agents"""
        return {
            "session_id": state.session_id,
            "topic": state.topic,
            "user_position": state.user_position,
            "ai_position": state.ai_position,
            "current_round": state.current_round,
            "phase": state.phase.value,
            "recent_messages": [
                {"role": msg.role.value, "content": msg.content, "agent": msg.agent_used}
                for msg in state.messages[-5:]  # Last 5 messages for context
            ],
            "total_messages": len(state.messages),
            "user_messages": len([msg for msg in state.messages if msg.role == MessageRole.USER]),
            "ai_messages": len([msg for msg in state.messages if msg.role == MessageRole.AI])
        }