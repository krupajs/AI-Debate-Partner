
# 🎯 Multi-Agent AI Debate Partner

An intelligent debate system powered by Google Gemini AI that uses multiple specialized agents to provide dynamic, engaging debate experiences. Features include voice input, real-time argument analysis, strategic coaching, and comprehensive performance evaluation.



## ✨ Features

### 🤖 Multi-Agent Architecture
- **Controller Agent**: Dynamically orchestrates debate flow using AI reasoning
- **Moderator Agent**: Maintains neutrality and manages structure
- **Debater Agents**: Generate arguments for both sides
- **Coach Agent**: Provides strategic tips and improvement suggestions
- **Feedback Agent**: Comprehensive performance evaluation
- **Memory Agent**: Context-aware conversation tracking

### 🎤 Voice Input
- Click-to-speak interface with real-time transcription
- Auto-send and continuous listening modes
- Visual feedback and animations
- Works on Chrome, Edge, and Safari

### 🧠 Intelligent Features
- Dynamic workflow selection at runtime
- Adapts to user's debate style and skill level
- Real-time argument strength analysis
- Educational coaching and feedback
- Debate transcript export

### Prerequisites
- Python 3.11 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))
- Modern web browser (Chrome, Edge, or Safari recommended)
## 📖 Usage

### Starting a Debate
1. Choose a topic category and difficulty level
2. Click "Start Debate Session"
3. Select your position (for or against)
4. Begin arguing with AI

### Using Voice Input
1. Click the 🎤 microphone button
2. Allow browser permission when prompted
3. Speak your argument
4. Text appears in real-time
5. Click stop or enable auto-send in settings

### Getting Feedback
- Click "Coach" button for strategic tips during debate
- Click "End Debate" for comprehensive evaluation
- Export transcript for review

## 🏗️ Architecture

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└──────┬──────┘
       │ HTTP/WebSocket
       │
┌──────▼──────────────────────────────┐
│       FastAPI Backend               │
│  ┌──────────────────────────────┐  │
│  │    Controller Agent          │  │
│  │  (Dynamic Orchestration)     │  │
│  └───────────┬──────────────────┘  │
│              │                      │
│  ┌───────────▼──────────────────┐  │
│  │  Specialized Agents:         │  │
│  │  • Moderator                 │  │
│  │  • Topic Generator           │  │
│  │  • Debater (For/Against)     │  │
│  │  • Coach                     │  │
│  │  • Feedback                  │  │
│  │  • Memory                    │  │
│  └──────────────────────────────┘  │
└─────────────┬───────────────────────┘
              │
       ┌──────▼──────┐
       │  Gemini AI  │
       └─────────────┘
```

## 🛠️ Technology Stack

**Backend:**
- FastAPI - Modern async Python web framework
- Google Gemini AI - Large language model
- Pydantic - Data validation
- Python-dotenv - Environment management

**Frontend:**
- Vanilla JavaScript - No framework dependencies
- Web Speech API - Voice recognition
- CSS3 - Modern animations and styling
- HTML5 - Semantic markup

## 📁 Project Structure

```
multi-agent-debate/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment template
│   ├── models/                # Data models
│   ├── agents/                # AI agent implementations
│   ├── services/              # Business logic
│   └── utils/                 # Helper functions
├── frontend/
│   ├── index.html             # Main UI
│   ├── css/
│   │   └── styles.css         # Styling
│   └── js/
│       ├── app.js             # Main controller
│       ├── debate.js          # API communication
│       ├── ui.js              # UI management
│       └── speech.js          # Voice recognition
├── .gitignore
├── .env.example
└── README.md
```


## 🎯 Features in Detail

### Agentic AI Architecture
Unlike traditional chatbots, this system uses **runtime decision-making**:
- Controller Agent analyzes context and chooses appropriate specialist
- No hardcoded conversation flows
- Adapts strategy based on user's argument strength and style
- Each debate is unique and personalized

### Voice Recognition
- Browser-based speech-to-text (no server-side processing)
- Real-time transcription display
- Configurable auto-send and continuous modes
- Privacy-focused (audio not stored)

### Educational Value
- Strategic coaching during debate
- Comprehensive performance evaluation
- Argument strength analysis
- Personalized improvement suggestions

<img width="1906" height="923" alt="image" src="https://github.com/user-attachments/assets/c0b2f4eb-f575-4545-85c0-c07d592f76a1" />


---

**Made with ❤️ using Python, FastAPI, and Google Gemini AI**

⭐ Star this repo if you find it useful!
