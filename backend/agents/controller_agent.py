"""Controller Agent - Orchestrates the entire debate flow"""

from typing import Dict, Any, List
import json
import asyncio
from agents.base_agent import BaseAgent, AgentRole
from models.debate_models import DebatePhase, MessageRole
import logging

logger = logging.getLogger(__name__)

class ControllerAgent(BaseAgent):
    """Main orchestrator that decides which agents to call and when"""
    
    def __init__(self, llm_service, memory_service, agents: Dict[AgentRole, BaseAgent]):
        super().__init__(AgentRole.CONTROLLER, llm_service, memory_service)
        self.agents = agents
        
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main decision-making logic for debate orchestration"""
        
        # Analyze current situation
        decision = await self._make_decision(task, context)
        
        # Execute the decided action
        response = await self._execute_decision(decision, context)
        
        return response
    
    async def _make_decision(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered decision making about what to do next"""
        
        decision_prompt = f"""
        You are the Controller Agent orchestrating a debate. Analyze the current situation and decide what action to take.
        
        Current Context:
        - Phase: {context.get('phase', 'setup')}
        - Round: {context.get('current_round', 0)}
        - Topic: {context.get('topic', 'Not set')}
        - User Position: {context.get('user_position', 'Not set')}
        - Recent Messages: {len(context.get('recent_messages', []))}
        
        User Input: "{user_input}"
        
        Available Actions:
        1. generate_topic - Use Topic Generator to create debate topic
        2. moderate_debate - Use Moderator for neutral announcements/transitions
        3. argue_for - Use For Debater to support user's position
        4. argue_against - Use Against Debater to oppose user's position  
        5. provide_feedback - Use Feedback Agent to evaluate arguments
        6. coach_user - Use Coach Agent to give tips
        7. store_memory - Use Memory Agent to save context
        8. end_debate - Conclude the debate session
        
        Respond with JSON format:
        {{
            "action": "action_name",
            "reasoning": "why this action was chosen",
            "agent_to_call": "agent_role",
            "specific_task": "detailed task for the agent",
            "confidence": 0.8,
            "metadata": {{"key": "value"}}
        }}
        """
        
        try:
            response = await self._call_llm(decision_prompt, context)
            decision = json.loads(response)
            return decision
        except json.JSONDecodeError:
            # Fallback decision if JSON parsing fails
            return self._fallback_decision(user_input, context)
        except Exception as e:
            logger.error(f"Decision making failed: {e}")
            return self._fallback_decision(user_input, context)
    
    async def _execute_decision(self, decision: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the decided action by calling appropriate agent"""
        
        action = decision.get("action", "moderate_debate")
        agent_role = decision.get("agent_to_call", "moderator")
        task = decision.get("specific_task", "Moderate the current situation")
        
        try:
            # Map string role to AgentRole enum
            agent_role_enum = AgentRole(agent_role)
            
            if agent_role_enum in self.agents:
                agent = self.agents[agent_role_enum]
                response = await agent.execute(task, context)
                
                # Add controller's reasoning to response
                response["controller_reasoning"] = decision.get("reasoning", "")
                response["action_taken"] = action
                
                return response
            else:
                logger.warning(f"Agent {agent_role} not found, using moderator")
                return await self.agents[AgentRole.MODERATOR].execute(task, context)
                
        except Exception as e:
            logger.error(f"Failed to execute decision: {e}")
            # Fallback to moderator
            return await self.agents[AgentRole.MODERATOR].execute(
                "Handle an error situation gracefully", context
            )
    
    def _fallback_decision(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback decision logic when AI decision fails"""
        
        phase = context.get("phase", "setup")
        
        if phase == "setup":
            if not context.get("topic"):
                return {
                    "action": "generate_topic",
                    "agent_to_call": "topic_generator",
                    "specific_task": "Generate an engaging debate topic",
                    "reasoning": "No topic set, need to generate one",
                    "confidence": 0.9
                }
        
        if user_input and len(user_input.strip()) > 10:
            # User provided substantial input, generate counter-argument
            user_position = context.get("user_position", "for")
            opponent_agent = "debater_against" if user_position == "for" else "debater_for"
            
            return {
                "action": "debate_response",
                "agent_to_call": opponent_agent,
                "specific_task": f"Provide counter-argument to: {user_input}",
                "reasoning": "User provided argument, need to respond",
                "confidence": 0.7
            }
        
        # Default to moderation
        return {
            "action": "moderate_debate",
            "agent_to_call": "moderator",
            "specific_task": "Moderate the current debate situation",
            "reasoning": "Default moderation action",
            "confidence": 0.5
        }
    
    def _get_role_prompt(self) -> str:
        return """You are the Controller Agent, the master orchestrator of debates. 
        Your role is to analyze the current situation and decide which specialized agent 
        should handle the next action. You think strategically about debate flow, 
        user engagement, and educational value. Make decisions that create dynamic, 
        engaging debates that adapt to user behavior in real-time."""