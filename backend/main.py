"""
Complete Working FastAPI Application
This version includes fallbacks if agent files are missing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uuid
from typing import Dict, Optional
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-Agent Debate System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
active_sessions: Dict = {}

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables!")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")

# Simple LLM caller
async def call_llm(prompt: str) -> str:
    """Call Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = await model.generate_content_async(prompt)
        
        if response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            return "I'm processing your request. Please try again."
            
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return f"I encountered an error: {str(e)}"

@app.get("/")
async def root():
    return {"message": "Multi-Agent Debate System API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    llm_healthy = False
    
    try:
        if GEMINI_API_KEY:
            model = genai.GenerativeModel('gemini-2.5-flash')
            test_response = model.generate_content("Say 'OK' if you work")
            llm_healthy = bool(test_response.candidates)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
    
    return {
        "status": "healthy",
        "services": {
            "api": True,
            "llm_service": llm_healthy,
            "gemini_key_present": bool(GEMINI_API_KEY)
        }
    }

@app.post("/api/debate")
async def handle_debate(request: dict):
    """Main debate endpoint"""
    try:
        action = request.get("action")
        
        if action == "start":
            return await start_debate(request)
        elif action == "continue":
            return await continue_debate(request)
        elif action == "end":
            return await end_debate(request)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
            
    except Exception as e:
        logger.error(f"Debate handling error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "detail": "Check backend logs for details"
            }
        )

async def start_debate(request: dict):
    """Start a new debate"""
    try:
        session_id = str(uuid.uuid4())
        topic_request = request.get("topic_request", {})
        
        # Generate or use custom topic
        custom_topic = topic_request.get("custom_topic")
        if custom_topic:
            topic = custom_topic
        else:
            category = topic_request.get("category", "general")
            difficulty = topic_request.get("difficulty", "moderate")
            
            prompt = f"""Generate a {difficulty} debate topic about {category}. 
            
            Provide just the topic as a clear statement that can be debated (not a question).
            Example: "Social media companies should be required to fact-check all posts"
            
            Your topic:"""
            
            topic = await call_llm(prompt)
            topic = topic.strip().strip('"').strip("'")
        
        # Create session state
        state = {
            "session_id": session_id,
            "topic": topic,
            "user_position": "",
            "ai_position": "",
            "phase": "setup",
            "current_round": 0,
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
        
        # Generate welcome message
        welcome_prompt = f"""You are a professional debate moderator. 
        
        The debate topic is: "{topic}"
        
        Welcome the user and ask them to choose their position (for or against this topic).
        Be encouraging and explain that you'll take the opposing position.
        Keep it to 2-3 sentences."""
        
        welcome_msg = await call_llm(welcome_prompt)
        
        # Store session
        active_sessions[session_id] = state
        
        logger.info(f"Started debate session: {session_id} with topic: {topic}")
        
        return {
            "success": True,
            "session_id": session_id,
            "current_state": state,
            "ai_response": {
                "agent_name": "Moderator",
                "content": welcome_msg,
                "reasoning": "Welcomed user and explained debate setup",
                "confidence": 0.9,
                "metadata": {}
            }
        }
        
    except Exception as e:
        logger.error(f"Start debate error: {e}", exc_info=True)
        raise

async def continue_debate(request: dict):
    """Continue an ongoing debate"""
    try:
        session_id = request.get("session_id")
        user_input = request.get("user_input", {})
        message = user_input.get("message", "")
        
        if not session_id or session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = active_sessions[session_id]
        
        # Add user message
        state["messages"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Detect position if not set
        if not state["user_position"]:
            message_lower = message.lower()
            if any(word in message_lower for word in ["support", "agree", "for", "yes", "favor"]):
                state["user_position"] = "for"
                state["ai_position"] = "against"
                state["phase"] = "opening"
                state["current_round"] = 1
            elif any(word in message_lower for word in ["oppose", "disagree", "against", "no"]):
                state["user_position"] = "against"
                state["ai_position"] = "for"
                state["phase"] = "opening"
                state["current_round"] = 1
        
        # Generate AI response based on context
        conversation_history = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in state["messages"][-5:]
        ])
        
        # Determine which agent/strategy to use
        if state["phase"] == "setup":
            prompt = f"""You are a debate moderator. The user said: "{message}"
            
            If they're choosing a position, acknowledge it and begin the debate.
            If unclear, ask them to clearly state if they are FOR or AGAINST: {state['topic']}"""
            agent_name = "Moderator"
            
        else:
            # Generate counter-argument
            ai_stance = "supporting" if state["ai_position"] == "for" else "opposing"
            
            prompt = f"""You are a skilled debater {ai_stance} the topic: "{state['topic']}"

Your position: {state["ai_position"]}
User's position: {state["user_position"]}

Recent conversation:
{conversation_history}

The user just said: "{message}"

Provide a strong, respectful counter-argument that:
1. Addresses their specific point
2. Presents evidence or examples
3. Uses logical reasoning
4. Challenges their position constructively
5. Is 100-200 words

Your response:"""
            agent_name = "Challenger" if state["ai_position"] == "against" else "Advocate"
        
        ai_response = await call_llm(prompt)
        
        # Add AI message
        state["messages"].append({
            "role": "ai",
            "content": ai_response,
            "agent": agent_name,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update round if needed
        user_msg_count = len([m for m in state["messages"] if m["role"] == "user"])
        if user_msg_count > state["current_round"] and state["phase"] != "setup":
            state["current_round"] = user_msg_count
        
        logger.info(f"Continued debate session: {session_id}, round: {state['current_round']}")
        
        return {
            "success": True,
            "session_id": session_id,
            "current_state": state,
            "ai_response": {
                "agent_name": agent_name,
                "content": ai_response,
                "reasoning": f"Generated {agent_name} response to user's argument",
                "confidence": 0.85,
                "metadata": {"round": state["current_round"]}
            }
        }
        
    except Exception as e:
        logger.error(f"Continue debate error: {e}", exc_info=True)
        raise

async def end_debate(request: dict):
    """End debate and provide evaluation"""
    try:
        session_id = request.get("session_id")
        
        if not session_id or session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = active_sessions[session_id]
        state["phase"] = "complete"
        
        # Generate evaluation
        conversation = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in state["messages"]
        ])
        
        eval_prompt = f"""You are an expert debate evaluator. Provide comprehensive feedback on this debate.

Topic: {state['topic']}
User's Position: {state['user_position']}
Rounds: {state['current_round']}

Full Conversation:
{conversation}

Provide evaluation covering:

**Argument Quality**
- Assess the strength of the user's main arguments
- Note use of evidence and examples

**Debate Skills**
- Structure and organization
- Response to counter-arguments
- Persuasiveness

**Strengths**
- What the user did well
- Effective techniques used

**Areas for Improvement**  
- Specific weaknesses
- Suggestions for stronger arguments

**Overall Summary**
- Brief performance summary
- Encouragement and next steps

Keep feedback constructive, specific, and encouraging."""
        
        evaluation = await call_llm(eval_prompt)
        
        logger.info(f"Ended debate session: {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "current_state": state,
            "ai_response": {
                "agent_name": "Evaluator",
                "content": evaluation,
                "reasoning": "Comprehensive debate evaluation completed",
                "confidence": 0.9,
                "metadata": {"type": "evaluation"}
            }
        }
        
    except Exception as e:
        logger.error(f"End debate error: {e}", exc_info=True)
        raise

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session state"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "state": active_sessions[session_id]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)