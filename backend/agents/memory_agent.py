# backend/agents/memory_agent.py
"""Memory Agent - Handles context storage and retrieval"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent, AgentRole
import logging
import json

logger = logging.getLogger(__name__)

class MemoryAgent(BaseAgent):
    """Manages conversation context and historical information"""
    
    def __init__(self, llm_service, memory_service=None):
        super().__init__(AgentRole.MEMORY, llm_service, memory_service)
        self.session_memories: Dict[str, List[Dict]] = {}
    
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute memory operations"""
        
        session_id = context.get("session_id", "default")
        
        if "store" in task.lower():
            return await self._store_memory(session_id, context)
        elif "retrieve" in task.lower():
            return await self._retrieve_memory(session_id, context)
        elif "summarize" in task.lower():
            return await self._summarize_context(session_id, context)
        else:
            return self._format_response(
                content="Memory operation completed",
                reasoning="Default memory response",
                confidence=0.7
            )
    
    async def _store_memory(self, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Store conversation context"""
        
        if session_id not in self.session_memories:
            self.session_memories[session_id] = []
        
        # Extract key information to store
        memory_entry = {
            "timestamp": context.get("timestamp"),
            "topic": context.get("topic"),
            "user_position": context.get("user_position"),
            "phase": context.get("phase"),
            "recent_messages": context.get("recent_messages", [])[-3:],  # Last 3 messages
            "metadata": context.get("metadata", {})
        }
        
        self.session_memories[session_id].append(memory_entry)
        
        # Keep only last 20 entries to prevent memory bloat
        if len(self.session_memories[session_id]) > 20:
            self.session_memories[session_id] = self.session_memories[session_id][-20:]
        
        return self._format_response(
            content="Context stored successfully",
            reasoning="Stored current debate context in memory",
            confidence=0.95,
            metadata={"stored_entries": len(self.session_memories[session_id])}
        )
    
    async def _retrieve_memory(self, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve stored context"""
        
        if session_id in self.session_memories:
            memories = self.session_memories[session_id]
            
            return self._format_response(
                content=json.dumps(memories[-5:], indent=2),  # Last 5 memory entries
                reasoning="Retrieved recent conversation history",
                confidence=0.9,
                metadata={"total_memories": len(memories)}
            )
        else:
            return self._format_response(
                content="No memories found for this session",
                reasoning="Session not found in memory store",
                confidence=0.8
            )
    
    async def _summarize_context(self, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate context summary using LLM"""
        
        memories = self.session_memories.get(session_id, [])
        
        if not memories:
            return self._format_response(
                content="No context available to summarize",
                reasoning="Empty memory for session",
                confidence=0.8
            )
        
        prompt = f"""
        Summarize the key points from this debate conversation:
        
        Topic: {context.get('topic', 'Unknown')}
        User Position: {context.get('user_position', 'Unknown')}
        
        Conversation History:
        {json.dumps(memories, indent=2)}
        
        Provide a concise summary covering:
        1. Main arguments presented by user
        2. Main counter-arguments presented by AI
        3. Key evidence or examples mentioned
        4. Current state of the debate
        5. Strengths and weaknesses observed
        
        Keep summary under 200 words.
        """
        
        try:
            summary = await self._call_llm(prompt, context)
            
            return self._format_response(
                content=summary,
                reasoning="Generated context summary from stored memories",
                confidence=0.85,
                metadata={"summarized_entries": len(memories)}
            )
            
        except Exception as e:
            logger.error(f"Context summarization failed: {e}")
            return self._format_response(
                content="Unable to generate context summary at this time",
                reasoning="Summary generation failed",
                confidence=0.3
            )
    
    def _get_role_prompt(self) -> str:
        return """You are the Memory Agent responsible for storing, retrieving,
        and summarizing conversation context. You help maintain continuity
        across long debates by keeping track of arguments, evidence, and
        the overall flow of discussion."""
