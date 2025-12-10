/**
 * UI Manager
 * Handles all user interface updates and interactions
 */

class UIManager {
    constructor(app) {
        this.app = app;
        this.messageCount = 0;
        this.toastCount = 0;
    }
    
    init() {
        console.log('UI Manager initialized');
        this.setupInitialState();
    }
    
    setupInitialState() {
        // Ensure setup panel is visible initially
        document.getElementById('setupPanel').style.display = 'block';
        document.getElementById('chatContainer').style.display = 'none';
        
        // Reset header stats
        this.updateHeaderStats({
            round: 0,
            phase: 'Setup',
            topic: 'Not Set'
        });
        
        // Reset agent info
        this.updateAgentInfo({
            name: 'System',
            emoji: '🤖',
            role: 'Ready to start',
            confidence: 0,
            reasoning: 'Waiting for debate to begin...'
        });
    }
    
    /**
     * Switch from setup to chat interface
     */
    switchToChat() {
        document.getElementById('setupPanel').style.display = 'none';
        document.getElementById('chatContainer').style.display = 'flex';
        
        // Focus on message input
        setTimeout(() => {
            document.getElementById('messageInput').focus();
        }, 100);
    }
    
    /**
     * Switch from chat to setup interface
     */
    switchToSetup() {
        document.getElementById('setupPanel').style.display = 'block';
        document.getElementById('chatContainer').style.display = 'none';
        
        this.setupInitialState();
    }
    
    /**
     * Update debate state in header
     */
    updateDebateState(state) {
        const formatted = this.app.debate.formatDebateState(state);
        
        this.updateHeaderStats({
            round: formatted.round,
            phase: formatted.phase,
            topic: formatted.topic
        });
    }
    
    /**
     * Update header statistics
     */
    updateHeaderStats(stats) {
        document.getElementById('roundCounter').textContent = stats.round;
        document.getElementById('phaseIndicator').textContent = stats.phase;
        document.getElementById('topicDisplay').textContent = this.truncateText(stats.topic, 50);
        document.getElementById('topicDisplay').title = stats.topic; // Full text on hover
    }
    
    /**
     * Add a message to the chat
     */
    addMessage(message) {
        const messagesList = document.getElementById('messagesList');
        const messageElement = this.createMessageElement(message);
        
        messagesList.appendChild(messageElement);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Increment counter
        this.messageCount++;
    }
    
    /**
     * Create a message DOM element
     */
    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.role}`;
        messageDiv.id = `message-${this.messageCount}`;
        
        let content = '';
        
        if (message.role === 'ai' || message.role === 'system') {
            const agentName = message.agent_name || 'AI';
            const agentEmoji = this.getAgentEmoji(agentName);
            
            content = `
                <div class="message-header">
                    <span class="agent-badge">${agentEmoji} ${agentName}</span>
                    <span class="message-time">${this.formatTime(message.timestamp)}</span>
                </div>
                <div class="message-content">${this.formatMessageContent(message.content)}</div>
            `;
        } else {
            content = `
                <div class="message-header">
                    <span class="message-time">${this.formatTime(message.timestamp)}</span>
                </div>
                <div class="message-content">${this.formatMessageContent(message.content)}</div>
            `;
        }
        
        messageDiv.innerHTML = content;
        
        // Add metadata classes for special message types
        if (message.metadata?.type) {
            messageDiv.classList.add(`message-type-${message.metadata.type}`);
        }
        
        return messageDiv;
    }
    
    /**
     * Format message content with basic markdown support
     */
    formatMessageContent(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
            .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
            .replace(/`(.*?)`/g, '<code>$1</code>') // Inline code
            .replace(/\n/g, '<br>') // Line breaks
            .replace(/(?:^|\n)(\d+\..*?)(?=\n|$)/g, '<ol><li>$1</li></ol>') // Simple numbered lists
            .replace(/(?:^|\n)([-*].*?)(?=\n|$)/g, '<ul><li>$1</li></ul>'); // Simple bullet lists
    }
    
    /**
     * Get emoji for agent type
     */
    getAgentEmoji(agentName) {
        const emojiMap = {
            'Controller': '🎯',
            'Moderator': '⚖️',
            'Topic Generator': '💡',
            'Advocate': '👍',
            'Challenger': '👎',
            'Evaluator': '📊',
            'Coach': '🏆',
            'Memory': '🧠',
            'AI': '🤖',
            'System': '⚙️'
        };
        
        return emojiMap[agentName] || '🤖';
    }
    
    /**
     * Update agent information panel
     */
    updateAgentInfo(agentInfo) {
        const info = this.app.debate.extractAgentInfo(agentInfo);
        
        if (!info) return;
        
        document.getElementById('agentName').textContent = info.name;
        document.getElementById('agentRole').textContent = info.role;
        document.getElementById('agentReasoning').textContent = info.reasoning;
        
        // Update confidence meter
        const confidence = Math.round(info.confidence * 100);
        document.getElementById('confidenceFill').style.width = `${confidence}%`;
        document.getElementById('confidenceValue').textContent = `${confidence}%`;
        
        // Update avatar
        document.querySelector('.agent-avatar').textContent = info.emoji;
    }
    
    /**
     * Clear all messages
     */
    clearMessages() {
        document.getElementById('messagesList').innerHTML = '';
        this.messageCount = 0;
    }
    
    /**
     * Show loading overlay
     */
    showLoading(show = true) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.add('active');
        } else {
            overlay.classList.remove('active');
        }
    }
    
    /**
     * Show evaluation modal
     */
    showEvaluation(evaluationContent) {
        const modal = document.getElementById('evaluationModal');
        const content = document.getElementById('evaluationContent');
        
        content.innerHTML = `
            <div class="evaluation-content">
                ${this.formatMessageContent(evaluationContent)}
            </div>
        `;
        
        modal.classList.add('active');
    }
    
    /**
     * Hide modal
     */
    hideModal() {
        document.getElementById('evaluationModal').classList.remove('active');
    }
    
    /**
     * Show toast notification
     */
    showToast(message, type = 'info', duration = 5000) {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        
        toast.className = `toast ${type}`;
        toast.id = `toast-${this.toastCount++}`;
        
        const icon = this.getToastIcon(type);
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">${icon}</span>
                <span>${message}</span>
            </div>
        `;
        
        container.appendChild(toast);
        
        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, duration);
        
        // Click to dismiss
        toast.addEventListener('click', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });
    }
    
    /**
     * Get icon for toast type
     */
    getToastIcon(type) {
        const icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        };
        
        return icons[type] || icons.info;
    }
    
    /**
     * Scroll chat to bottom
     */
    scrollToBottom() {
        const messagesArea = document.getElementById('messagesArea');
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }
    
    /**
     * Format timestamp for display
     */
    formatTime(timestamp) {
        if (!timestamp) return '';
        
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    /**
     * Truncate text with ellipsis
     */
    truncateText(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }
    
    /**
     * Enable/disable input elements
     */
    setInputEnabled(enabled) {
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const coachBtn = document.getElementById('coachBtn');
        
        messageInput.disabled = !enabled;
        sendBtn.disabled = !enabled;
        coachBtn.disabled = !enabled;
    }
    
    /**
     * Update button states based on debate phase
     */
    updateButtonStates(phase) {
        const endBtn = document.getElementById('endDebateBtn');
        const coachBtn = document.getElementById('coachBtn');
        
        if (phase === 'setup') {
            endBtn.disabled = true;
            coachBtn.disabled = true;
        } else if (phase === 'complete') {
            endBtn.disabled = true;
            coachBtn.disabled = true;
        } else {
            endBtn.disabled = false;
            coachBtn.disabled = false;
        }
    }
    
    /**
     * Show confirmation dialog
     */
    showConfirmation(message, callback) {
        if (confirm(message)) {
            callback();
        }
    }
    
    /**
     * Animate message appearance
     */
    animateMessage(messageElement) {
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            messageElement.style.transition = 'all 0.3s ease-out';
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        }, 10);
    }
    
    /**
     * Handle responsive design adjustments
     */
    handleResize() {
        const width = window.innerWidth;
        
        if (width <= 768) {
            // Mobile adjustments
            this.adjustForMobile();
        } else {
            // Desktop adjustments
            this.adjustForDesktop();
        }
    }
    
    adjustForMobile() {
        // Mobile-specific UI adjustments
        const header = document.querySelector('.header-stats');
        if (header) {
            header.style.fontSize = '0.8rem';
        }
    }
    
    adjustForDesktop() {
        // Desktop-specific UI adjustments
        const header = document.querySelector('.header-stats');
        if (header) {
            header.style.fontSize = '1rem';
        }
    }
    
    /**
     * Initialize responsive handlers
     */
    initResponsive() {
        window.addEventListener('resize', () => {
            this.handleResize();
        });
        
        // Initial check
        this.handleResize();
    }
    
    /**
     * Show debug information (for development)
     */
    showDebugInfo(data) {
        if (this.app.debug) {
            console.log('Debug Info:', data);
            
            // Optionally show in UI
            this.showToast(`Debug: ${JSON.stringify(data)}`, 'info', 10000);
        }
    }
    
    /**
     * Export debate transcript
     */
    exportDebateTranscript() {
        const messages = document.querySelectorAll('.message');
        let transcript = '';
        
        messages.forEach(msg => {
            const role = msg.classList.contains('user') ? 'You' : 'AI';
            const content = msg.querySelector('.message-content').textContent;
            const time = msg.querySelector('.message-time')?.textContent || '';
            
            transcript += `[${time}] ${role}: ${content}\n\n`;
        });
        
        // Create download
        const blob = new Blob([transcript], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `debate-transcript-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        this.showToast('Transcript exported successfully!', 'success');
    }
    
    /**
     * Copy debate summary to clipboard
     */
    async copyDebateSummary() {
        if (!this.app.currentState) {
            this.showToast('No active debate to copy', 'warning');
            return;
        }
        
        const summary = this.app.debate.generateSummary(this.app.currentState);
        
        try {
            await navigator.clipboard.writeText(summary);
            this.showToast('Summary copied to clipboard!', 'success');
        } catch (error) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = summary;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            this.showToast('Summary copied to clipboard!', 'success');
        }
    }
    
    /**
     * Initialize keyboard shortcuts
     */
    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to send message
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                if (document.getElementById('messageInput').value.trim()) {
                    this.app.sendMessage();
                }
            }
            
            // Ctrl/Cmd + Shift + C to get coaching
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
                e.preventDefault();
                this.app.getCoaching();
            }
            
            // Escape to close modal
            if (e.key === 'Escape') {
                this.hideModal();
            }
        });
    }
    
    /**
     * Show typing indicator
     */
    showTypingIndicator(show = true) {
        let indicator = document.getElementById('typingIndicator');
        
        if (show) {
            if (!indicator) {
                indicator = document.createElement('div');
                indicator.id = 'typingIndicator';
                indicator.className = 'message ai typing';
                indicator.innerHTML = `
                    <div class="message-header">
                        <span class="agent-badge">🤖 AI</span>
                    </div>
                    <div class="message-content">
                        <div class="typing-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                `;
                
                // Add CSS for typing animation
                const style = document.createElement('style');
                style.textContent = `
                    .typing-dots {
                        display: flex;
                        gap: 4px;
                        align-items: center;
                    }
                    .typing-dots span {
                        width: 8px;
                        height: 8px;
                        border-radius: 50%;
                        background-color: #666;
                        animation: typing 1.4s infinite ease-in-out;
                    }
                    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
                    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
                    @keyframes typing {
                        0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
                        40% { transform: scale(1); opacity: 1; }
                    }
                `;
                document.head.appendChild(style);
                
                document.getElementById('messagesList').appendChild(indicator);
                this.scrollToBottom();
            }
        } else {
            if (indicator) {
                indicator.remove();
            }
        }
    }
    
    /**
     * Initialize all UI components
     */
    initializeComponents() {
        this.initResponsive();
        this.initKeyboardShortcuts();
        
        // Add export functionality to quick actions
        const exportBtn = document.createElement('button');
        exportBtn.className = 'quick-action-btn';
        exportBtn.innerHTML = '<span>💾</span> Export';
        exportBtn.addEventListener('click', () => this.exportDebateTranscript());
        
        const quickActions = document.querySelector('.quick-actions');
        if (quickActions) {
            quickActions.appendChild(exportBtn);
        }
        
        // Add copy summary functionality
        const copyBtn = document.createElement('button');
        copyBtn.className = 'quick-action-btn';
        copyBtn.innerHTML = '<span>📋</span> Copy Summary';
        copyBtn.addEventListener('click', () => this.copyDebateSummary());
        
        if (quickActions) {
            quickActions.appendChild(copyBtn);
        }
    }
}