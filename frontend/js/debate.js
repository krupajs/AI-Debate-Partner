/**
 * Debate Manager
 * Handles all debate-related API communications
 */

class DebateManager {
    constructor(app) {
        this.app = app;
        this.apiUrl = app.apiBaseUrl;
    }
    
    /**
     * Start a new debate session
     */
    async startDebate(topicRequest) {
        try {
            const response = await fetch(`${this.apiUrl}/debate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'start',
                    topic_request: topicRequest
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            
            const result = await response.json();
            return result;
            
        } catch (error) {
            console.error('Start debate error:', error);
            throw error;
        }
    }
    
    /**
     * Continue an existing debate with a user message
     */
    async continueDebate(sessionId, message) {
        try {
            const response = await fetch(`${this.apiUrl}/debate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'continue',
                    session_id: sessionId,
                    user_input: {
                        session_id: sessionId,
                        message: message,
                        voice_input: false
                    }
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            
            const result = await response.json();
            return result;
            
        } catch (error) {
            console.error('Continue debate error:', error);
            throw error;
        }
    }
    
    /**
     * End the current debate session
     */
    async endDebate(sessionId) {
        try {
            const response = await fetch(`${this.apiUrl}/debate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'end',
                    session_id: sessionId
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            
            const result = await response.json();
            return result;
            
        } catch (error) {
            console.error('End debate error:', error);
            throw error;
        }
    }
    
    /**
     * Get current session state
     */
    async getSession(sessionId) {
        try {
            const response = await fetch(`${this.apiUrl}/session/${sessionId}`);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            
            const result = await response.json();
            return result;
            
        } catch (error) {
            console.error('Get session error:', error);
            throw error;
        }
    }
    
    /**
     * Delete a session
     */
    async deleteSession(sessionId) {
        try {
            const response = await fetch(`${this.apiUrl}/session/${sessionId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            
            const result = await response.json();
            return result;
            
        } catch (error) {
            console.error('Delete session error:', error);
            throw error;
        }
    }
    
    /**
     * Send a message via WebSocket (for real-time communication)
     */
    sendWebSocketMessage(message) {
        if (this.app.websocket && this.app.websocket.readyState === WebSocket.OPEN) {
            this.app.websocket.send(JSON.stringify({
                message: message,
                timestamp: new Date().toISOString()
            }));
        }
    }
    
    /**
     * Format debate state for display
     */
    formatDebateState(state) {
        return {
            topic: state.topic || 'No topic set',
            userPosition: state.user_position || 'Not chosen',
            aiPosition: state.ai_position || 'Not set',
            phase: this.formatPhase(state.phase),
            round: state.current_round || 0,
            messageCount: state.messages ? state.messages.length : 0
        };
    }
    
    /**
     * Format phase names for display
     */
    formatPhase(phase) {
        const phaseMap = {
            'setup': 'Setup',
            'opening': 'Opening Arguments',
            'rebuttal': 'Rebuttal Phase',
            'closing': 'Closing Statements',
            'evaluation': 'Evaluation',
            'complete': 'Complete'
        };
        
        return phaseMap[phase] || phase;
    }
    
    /**
     * Extract agent information from response
     */
    extractAgentInfo(response) {
        if (!response) return null;
        
        const agentMap = {
            'controller': { name: 'Controller', emoji: '🎯', role: 'Orchestrating debate flow' },
            'moderator': { name: 'Moderator', emoji: '⚖️', role: 'Managing debate structure' },
            'topic_generator': { name: 'Topic Generator', emoji: '💡', role: 'Creating debate topics' },
            'debater_for': { name: 'Advocate', emoji: '👍', role: 'Supporting arguments' },
            'debater_against': { name: 'Challenger', emoji: '👎', role: 'Challenging arguments' },
            'feedback': { name: 'Evaluator', emoji: '📊', role: 'Providing feedback' },
            'coach': { name: 'Coach', emoji: '🏆', role: 'Offering strategic tips' },
            'memory': { name: 'Memory', emoji: '🧠', role: 'Managing context' }
        };
        
        const agentName = response.agent_name || 'moderator';
        const agentInfo = agentMap[agentName] || agentMap['moderator'];
        
        return {
            name: agentInfo.name,
            emoji: agentInfo.emoji,
            role: agentInfo.role,
            confidence: response.confidence || 0,
            reasoning: response.reasoning || 'Processing...',
            metadata: response.metadata || {}
        };
    }
    
    /**
     * Validate message before sending
     */
    validateMessage(message) {
        if (!message || typeof message !== 'string') {
            return { valid: false, error: 'Message is required' };
        }
        
        if (message.trim().length === 0) {
            return { valid: false, error: 'Message cannot be empty' };
        }
        
        if (message.length > 2000) {
            return { valid: false, error: 'Message is too long (max 2000 characters)' };
        }
        
        return { valid: true };
    }
    
    /**
     * Get debate statistics
     */
    getDebateStats(state) {
        if (!state || !state.messages) {
            return {
                totalMessages: 0,
                userMessages: 0,
                aiMessages: 0,
                rounds: 0,
                duration: 0
            };
        }
        
        const userMessages = state.messages.filter(m => m.role === 'user').length;
        const aiMessages = state.messages.filter(m => m.role === 'ai').length;
        
        // Calculate duration if timestamps are available
        let duration = 0;
        if (state.created_at && state.updated_at) {
            const start = new Date(state.created_at);
            const end = new Date(state.updated_at);
            duration = Math.round((end - start) / 1000 / 60); // minutes
        }
        
        return {
            totalMessages: state.messages.length,
            userMessages,
            aiMessages,
            rounds: state.current_round || 0,
            duration
        };
    }
    
    /**
     * Generate debate summary for sharing
     */
    generateSummary(state) {
        const stats = this.getDebateStats(state);
        const formatted = this.formatDebateState(state);
        
        return `
Debate Summary:
Topic: ${formatted.topic}
Your Position: ${formatted.userPosition}
AI Position: ${formatted.aiPosition}
Phase: ${formatted.phase}
Rounds: ${stats.rounds}
Messages Exchanged: ${stats.totalMessages}
Duration: ${stats.duration} minutes

This debate was powered by Multi-Agent AI with dynamic strategy selection.
        `.trim();
    }
}