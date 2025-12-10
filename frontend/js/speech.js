/**
 * Speech Recognition Manager
 * Handles voice input using Web Speech API
 */

class SpeechManager {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.isSupported = false;
        this.finalTranscript = '';
        this.interimTranscript = '';
        
        this.initSpeechRecognition();
    }
    
    initSpeechRecognition() {
        // Check for browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.warn('Speech Recognition not supported in this browser');
            this.isSupported = false;
            return;
        }
        
        this.isSupported = true;
        
        // Initialize recognition
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';
        this.recognition.maxAlternatives = 1;
        
        // Event handlers
        this.recognition.onstart = () => {
            console.log('Speech recognition started');
            this.isListening = true;
            this.finalTranscript = '';
            this.interimTranscript = '';
            this.updateUI('listening');
        };
        
        this.recognition.onresult = (event) => {
            this.interimTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                
                if (event.results[i].isFinal) {
                    this.finalTranscript += transcript + ' ';
                } else {
                    this.interimTranscript += transcript;
                }
            }
            
            // Update the text area with current transcript
            this.updateTextArea();
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            
            let errorMessage = 'Speech recognition error';
            switch (event.error) {
                case 'no-speech':
                    errorMessage = 'No speech detected. Please try again.';
                    break;
                case 'audio-capture':
                    errorMessage = 'Microphone not accessible. Please check permissions.';
                    break;
                case 'not-allowed':
                    errorMessage = 'Microphone permission denied. Please enable it in browser settings.';
                    break;
                case 'network':
                    errorMessage = 'Network error occurred. Please check your connection.';
                    break;
                default:
                    errorMessage = `Error: ${event.error}`;
            }
            
            this.showError(errorMessage);
            this.stop();
        };
        
        this.recognition.onend = () => {
            console.log('Speech recognition ended');
            this.isListening = false;
            this.updateUI('stopped');
            
            // If we have a transcript, finalize it
            if (this.finalTranscript.trim()) {
                this.finalizeTranscript();
            }
        };
    }
    
    start() {
        if (!this.isSupported) {
            this.showError('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return false;
        }
        
        if (this.isListening) {
            console.log('Already listening');
            return false;
        }
        
        try {
            this.finalTranscript = '';
            this.interimTranscript = '';
            this.recognition.start();
            return true;
        } catch (error) {
            console.error('Failed to start speech recognition:', error);
            this.showError('Failed to start voice input. Please try again.');
            return false;
        }
    }
    
    stop() {
        if (!this.isListening) {
            return;
        }
        
        try {
            this.recognition.stop();
        } catch (error) {
            console.error('Failed to stop speech recognition:', error);
        }
    }
    
    toggle() {
        if (this.isListening) {
            this.stop();
        } else {
            this.start();
        }
    }
    
    updateTextArea() {
        const messageInput = document.getElementById('messageInput');
        if (!messageInput) return;
        
        // Combine final and interim transcripts
        const fullTranscript = this.finalTranscript + this.interimTranscript;
        messageInput.value = fullTranscript;
        
        // Update listening indicator with interim text
        const listeningText = document.getElementById('listeningText');
        if (listeningText && this.interimTranscript) {
            listeningText.textContent = `Listening: "${this.interimTranscript}"`;
        } else if (listeningText) {
            listeningText.textContent = 'Listening...';
        }
    }
    
    finalizeTranscript() {
        const messageInput = document.getElementById('messageInput');
        if (!messageInput) return;
        
        messageInput.value = this.finalTranscript.trim();
        
        // Auto-focus on the text area for editing
        messageInput.focus();
        
        // Move cursor to end
        messageInput.selectionStart = messageInput.selectionEnd = messageInput.value.length;
        
        // Optional: Auto-send after voice input (uncomment to enable)
        // setTimeout(() => {
        //     if (window.debateApp && messageInput.value.trim()) {
        //         window.debateApp.sendMessage();
        //     }
        // }, 500);
    }
    
    updateUI(state) {
        const voiceBtn = document.getElementById('voiceBtn');
        const voiceIcon = document.getElementById('voiceIcon');
        const voiceText = document.getElementById('voiceText');
        const listeningIndicator = document.getElementById('listeningIndicator');
        
        if (!voiceBtn) return;
        
        switch (state) {
            case 'listening':
                voiceBtn.classList.add('listening');
                voiceBtn.classList.remove('processing');
                if (voiceIcon) voiceIcon.textContent = '🎙️';
                if (voiceText) voiceText.textContent = 'Stop';
                if (listeningIndicator) listeningIndicator.classList.add('active');
                break;
                
            case 'processing':
                voiceBtn.classList.add('processing');
                voiceBtn.classList.remove('listening');
                if (voiceIcon) voiceIcon.textContent = '⏳';
                if (voiceText) voiceText.textContent = 'Processing';
                if (listeningIndicator) listeningIndicator.classList.remove('active');
                break;
                
            case 'stopped':
            default:
                voiceBtn.classList.remove('listening', 'processing');
                if (voiceIcon) voiceIcon.textContent = '🎤';
                if (voiceText) voiceText.textContent = 'Voice';
                if (listeningIndicator) listeningIndicator.classList.remove('active');
                break;
        }
    }
    
    showError(message) {
        // Use the app's toast notification system if available
        if (window.debateApp && window.debateApp.ui) {
            window.debateApp.ui.showToast(message, 'error');
        } else {
            alert(message);
        }
    }
    
    checkMicrophonePermission() {
        if (!navigator.permissions) {
            return Promise.resolve('prompt');
        }
        
        return navigator.permissions.query({ name: 'microphone' })
            .then(permissionStatus => {
                return permissionStatus.state; // 'granted', 'denied', or 'prompt'
            })
            .catch(() => 'prompt');
    }
    
    async requestMicrophonePermission() {
        try {
            // Try to get microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Stop the stream immediately (we just needed permission)
            stream.getTracks().forEach(track => track.stop());
            
            return true;
        } catch (error) {
            console.error('Microphone permission denied:', error);
            this.showError('Microphone access denied. Please enable it in your browser settings.');
            return false;
        }
    }
}

// Initialize speech manager when DOM is ready
let speechManager = null;

document.addEventListener('DOMContentLoaded', () => {
    speechManager = new SpeechManager();
    
    // Add voice button click handler
    const voiceBtn = document.getElementById('voiceBtn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', async () => {
            if (!speechManager.isSupported) {
                speechManager.showError('Speech recognition is not supported in your browser. Try Chrome, Edge, or Safari.');
                return;
            }
            
            // Check and request permission if needed
            const permissionState = await speechManager.checkMicrophonePermission();
            
            if (permissionState === 'denied') {
                speechManager.showError('Microphone permission is denied. Please enable it in your browser settings.');
                return;
            }
            
            if (permissionState === 'prompt') {
                const granted = await speechManager.requestMicrophonePermission();
                if (!granted) return;
            }
            
            // Toggle speech recognition
            speechManager.toggle();
        });
        
        // Show tooltip if not supported
        if (!speechManager.isSupported) {
            voiceBtn.title = 'Voice input not supported in this browser';
            voiceBtn.style.opacity = '0.5';
        }
    }
});

// Export for use in other modules
window.speechManager = speechManager;