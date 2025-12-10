/**
 * Main Application Controller
 * Handles initialization and coordination between modules
 */

class DebateApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api';
        this.currentSessionId = null;
        this.currentState = null;
        this.websocket = null;
        
        // Initialize modules
        this.debate = new DebateManager(this);
        this.ui = new UIManager(this);
        
        this.init();
    }
    
    async init() {
        console.log('Initializing Debate App...');
        
        // Check backend health
        try {
            const response = await fetch(`${this.apiBaseUrl.replace('/api', '')}/health`);
            const health = await response.json();
            
            if (!health.services.llm_service) {
                this.ui.showToast('Warning: LLM service not available. Please check API key.', 'warning');
            }
        } catch (error) {
            console.error('Backend health check failed:', error);
            this.ui.showToast('Backend connection failed. Please ensure the server is running.', 'error');
        }
        
        // Initialize UI
        this.ui.init();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('Debate App initialized successfully');
    }
    
    setupEventListeners() {
        // Start debate button
        document.getElementById('startDebateBtn').addEventListener('click', () => {
            this.startNewDebate();
        });
        
        // Send message button
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Message input (Enter key)
        document.getElementById('messageInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Voice button is handled in speech.js
        // But we can add additional logic here if needed
        
        // Coach button
        document.getElementById('coachBtn').addEventListener('click', () => {
            this.getCoaching();
        });
        
        // End debate button
        document.getElementById('endDebateBtn').addEventListener('click', () => {
            this.endDebate();
        });
        
        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.getAttribute('data-action');
                this.handleQuickAction(action);
            });
        });
        
        // Modal close buttons
        document.getElementById('closeModalBtn').addEventListener('click', () => {
            this.ui.hideModal();
        });
        
        document.getElementById('closeEvalBtn').addEventListener('click', () => {
            this.ui.hideModal();
        });
        
        document.getElementById('newDebateBtn').addEventListener('click', () => {
            this.ui.hideModal();
            this.resetToSetup();
        });
        
        // Global error handling
        window.addEventListener('error', (e) => {
            console.error('Global error:', e);
            this.ui.showToast('An unexpected error occurred', 'error');
        });
    }
    
    async startNewDebate() {
        const category = document.getElementById('topicSelect').value;
        const difficulty = document.getElementById('difficultySelect').value;
        const customTopic = document.getElementById('customTopic').value.trim();
        
        try {
            this.ui.showLoading(true);
            
            const topicRequest = {
                category: category,
                difficulty: difficulty,
                custom_topic: customTopic || null
            };
            
            const result = await this.debate.startDebate(topicRequest);
            
            if (result.success) {
                this.currentSessionId = result.session_id;
                this.currentState = result.current_state;
                
                // Switch to chat interface
                this.ui.switchToChat();
                
                // Update UI with initial state
                this.ui.updateDebateState(result.current_state);
                
                // Add initial AI message
                if (result.ai_response) {
                    this.ui.addMessage({
                        role: 'ai',
                        content: result.ai_response.content,
                        agent_name: result.ai_response.agent_name,
                        timestamp: new Date()
                    });
                    
                    this.ui.updateAgentInfo(result.ai_response);
                }
                
                this.ui.showToast('Debate started successfully!', 'success');
            } else {
                throw new Error(result.error || 'Failed to start debate');
            }
            
        } catch (error) {
            console.error('Error starting debate:', error);
            this.ui.showToast(`Failed to start debate: ${error.message}`, 'error');
        } finally {
            this.ui.showLoading(false);
        }
    }
    
    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || !this.currentSessionId) {
            return;
        }
        
        try {
            // Disable input and show loading
            messageInput.disabled = true;
            document.getElementById('sendBtn').disabled = true;
            this.ui.showLoading(true);
            
            // Add user message to UI immediately
            this.ui.addMessage({
                role: 'user',
                content: message,
                timestamp: new Date()
            });
            
            // Clear input
            messageInput.value = '';
            
            // Send to backend
            const result = await this.debate.continueDebate(this.currentSessionId, message);
            
            if (result.success) {
                this.currentState = result.current_state;
                
                // Update UI state
                this.ui.updateDebateState(result.current_state);
                
                // Add AI response
                if (result.ai_response) {
                    this.ui.addMessage({
                        role: 'ai',
                        content: result.ai_response.content,
                        agent_name: result.ai_response.agent_name,
                        timestamp: new Date(),
                        metadata: result.ai_response.metadata
                    });
                    
                    this.ui.updateAgentInfo(result.ai_response);
                }
                
            } else {
                throw new Error(result.error || 'Failed to send message');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.ui.showToast(`Failed to send message: ${error.message}`, 'error');
        } finally {
            // Re-enable input
            messageInput.disabled = false;
            document.getElementById('sendBtn').disabled = false;
            this.ui.showLoading(false);
            messageInput.focus();
        }
    }
    
    async getCoaching() {
        if (!this.currentSessionId || !this.currentState) {
            this.ui.showToast('No active debate session', 'warning');
            return;
        }
        
        try {
            this.ui.showLoading(true);
            
            // Make a special request for coaching
            const result = await this.debate.continueDebate(
                this.currentSessionId, 
                "Please provide coaching tips for improving my debate performance"
            );
            
            if (result.success && result.ai_response) {
                this.ui.addMessage({
                    role: 'ai',
                    content: result.ai_response.content,
                    agent_name: 'Coach',
                    timestamp: new Date(),
                    metadata: { type: 'coaching' }
                });
                
                this.ui.updateAgentInfo(result.ai_response);
                this.ui.showToast('Coaching tips provided!', 'success');
            }
            
        } catch (error) {
            console.error('Error getting coaching:', error);
            this.ui.showToast(`Failed to get coaching: ${error.message}`, 'error');
        } finally {
            this.ui.showLoading(false);
        }
    }
    
    async endDebate() {
        if (!this.currentSessionId) {
            this.ui.showToast('No active debate session', 'warning');
            return;
        }
        
        try {
            this.ui.showLoading(true);
            
            const result = await this.debate.endDebate(this.currentSessionId);
            
            if (result.success) {
                this.currentState = result.current_state;
                
                // Show evaluation in modal
                if (result.ai_response) {
                    this.ui.showEvaluation(result.ai_response.content);
                }
                
                this.ui.showToast('Debate ended. Evaluation ready!', 'success');
                
            } else {
                throw new Error(result.error || 'Failed to end debate');
            }
            
        } catch (error) {
            console.error('Error ending debate:', error);
            this.ui.showToast(`Failed to end debate: ${error.message}`, 'error');
        } finally {
            this.ui.showLoading(false);
        }
    }
    
    async handleQuickAction(action) {
        if (!this.currentSessionId) {
            this.ui.showToast('No active debate session', 'warning');
            return;
        }
        
        try {
            this.ui.showLoading(true);
            
            let message = '';
            switch (action) {
                case 'feedback':
                    message = 'Please provide detailed feedback on my debate performance so far';
                    break;
                case 'summary':
                    message = 'Please summarize the key points and current state of our debate';
                    break;
                case 'new-topic':
                    this.resetToSetup();
                    return;
                default:
                    return;
            }
            
            const result = await this.debate.continueDebate(this.currentSessionId, message);
            
            if (result.success && result.ai_response) {
                this.ui.addMessage({
                    role: 'ai',
                    content: result.ai_response.content,
                    agent_name: result.ai_response.agent_name,
                    timestamp: new Date(),
                    metadata: { type: action }
                });
                
                this.ui.updateAgentInfo(result.ai_response);
            }
            
        } catch (error) {
            console.error('Error handling quick action:', error);
            this.ui.showToast(`Failed to execute action: ${error.message}`, 'error');
        } finally {
            this.ui.showLoading(false);
        }
    }
    
    resetToSetup() {
        // Reset application state
        this.currentSessionId = null;
        this.currentState = null;
        
        // Reset UI
        this.ui.switchToSetup();
        this.ui.clearMessages();
        
        // Clear form
        document.getElementById('customTopic').value = '';
        document.getElementById('topicSelect').value = 'general';
        document.getElementById('difficultySelect').value = 'moderate';
        
        this.ui.showToast('Ready to start a new debate!', 'success');
    }
    
    // WebSocket functionality (for future real-time features)
    initializeWebSocket() {
        if (!this.currentSessionId) return;
        
        try {
            this.websocket = new WebSocket(`ws://localhost:8000/ws/${this.currentSessionId}`);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.websocket = null;
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    }
    
    handleWebSocketMessage(data) {
        if (data.type === 'debate_response' && data.data.ai_response) {
            this.ui.addMessage({
                role: 'ai',
                content: data.data.ai_response.content,
                agent_name: data.data.ai_response.agent_name,
                timestamp: new Date()
            });
            
            this.ui.updateAgentInfo(data.data.ai_response);
        }
    }
    
    closeWebSocket() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.debateApp = new DebateApp();
});