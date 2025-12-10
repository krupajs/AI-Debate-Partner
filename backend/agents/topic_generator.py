# backend/agents/topic_generator.py
"""Topic Generator Agent - Creates engaging debate topics"""

from typing import Dict, Any
from agents.base_agent import BaseAgent, AgentRole
import logging
import random

logger = logging.getLogger(__name__)

class TopicGeneratorAgent(BaseAgent):
    """Generates compelling debate topics based on user preferences"""
    
    def __init__(self, llm_service, memory_service=None):
        super().__init__(AgentRole.TOPIC_GENERATOR, llm_service, memory_service)
    
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate debate topics"""
        
        topic_request = context.get("topic_request", {})
        category = topic_request.get("category", "general")
        difficulty = topic_request.get("difficulty", "moderate")
        
        prompt = f"""
        Generate an engaging debate topic suitable for educational debate practice.
        
        Requirements:
        - Category: {category}
        - Difficulty: {difficulty}
        - Should have clear "for" and "against" positions
        - Should be current and relevant
        - Should encourage critical thinking
        - Should be suitable for educational purposes
        
        Task: {task}
        
        Provide just the topic statement, phrased as a proposition that can be debated.
        Examples:
        - "Social media companies should be legally required to fact-check all posts"
        - "Universal basic income should be implemented globally"
        - "Space exploration funding should be redirected to climate change research"
        
        Generate one clear, debatable topic (not a question, but a statement to argue for/against):
        """
        
        try:
            response = await self._call_llm(prompt, context)
            
            # Clean up the response to ensure it's just the topic
            topic = response.strip().strip('"').strip("'")
            
            return self._format_response(
                content=topic,
                reasoning=f"Generated {difficulty} debate topic in {category} category",
                confidence=0.85,
                metadata={
                    "category": category,
                    "difficulty": difficulty,
                    "type": "generated_topic"
                }
            )
            
        except Exception as e:
            logger.error(f"Topic generation failed: {e}")
            # Fallback topics
            fallback_topics = [
                "Artificial intelligence should be regulated by international law",
                "Social media has done more harm than good to society",
                "Climate change policies should take priority over economic growth",
                "Online privacy is more important than national security"
            ]
            
            return self._format_response(
                content=random.choice(fallback_topics),
                reasoning="Fallback topic due to generation error",
                confidence=0.6
            )
    
    def _get_role_prompt(self) -> str:
        return """You are a creative topic generator for educational debates.
        You create engaging, balanced topics that encourage critical thinking
        and have clear positions that can be argued from multiple sides.
        You focus on current, relevant issues that help users develop their
        argumentation and reasoning skills."""
