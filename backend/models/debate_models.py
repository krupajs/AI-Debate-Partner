"""Data models for the debate system"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class DebatePhase(str, Enum):
    SETUP = "setup"
    OPENING = "opening"
    REBUTTAL = "rebuttal"
    CLOSING = "closing"
    EVALUATION = "evaluation"
    COMPLETE = "complete"

class MessageRole(str, Enum):
    USER = "user"
    AI = "ai"
    MODERATOR = "moderator"
    SYSTEM = "system"

class ArgumentStrength(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    EXCELLENT = "excellent"

class DebateMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_used: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DebateState(BaseModel):
    session_id: str
    topic: str = ""
    user_position: str = ""
    ai_position: str = ""
    current_round: int = 0
    phase: DebatePhase = DebatePhase.SETUP
    messages: List[DebateMessage] = Field(default_factory=list)
    context_summary: str = ""
    user_score: int = 0
    ai_score: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class TopicRequest(BaseModel):
    category: Optional[str] = None
    difficulty: Optional[str] = "moderate"  # easy, moderate, hard
    custom_topic: Optional[str] = None

class UserInput(BaseModel):
    session_id: str
    message: str
    voice_input: Optional[bool] = False

class AgentResponse(BaseModel):
    agent_name: str
    content: str
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DebateEvaluation(BaseModel):
    user_arguments: List[Dict[str, Any]]
    ai_arguments: List[Dict[str, Any]]
    user_strengths: List[str]
    user_weaknesses: List[str]
    ai_strengths: List[str]
    ai_weaknesses: List[str]
    overall_winner: str
    score_breakdown: Dict[str, int]
    coaching_tips: List[str]
    summary: str

class DebateRequest(BaseModel):
    action: str  # "start", "continue", "end"
    session_id: Optional[str] = None
    topic_request: Optional[TopicRequest] = None
    user_input: Optional[UserInput] = None

class DebateResponse(BaseModel):
    success: bool
    session_id: str
    current_state: DebateState
    ai_response: Optional[AgentResponse] = None
    evaluation: Optional[DebateEvaluation] = None
    error: Optional[str] = None