# AI Mental Health Companion 🧠

An empathetic AI chatbot designed to support mental well-being through natural conversations, mood analysis, and personalized habit suggestions. Built with Google's Gemini API and Firestore for secure, scalable mental health support.

## 🌟 Features

### ✅ Core Features (Implemented)
- **Empathetic Chatbot**: Natural, supportive conversations using Google's Gemini 2.0 Flash model
- **Secure Backend**: Firestore integration with user data isolation and session management
- **Interactive UI**: Streamlit-based chat interface with conversation history
- **Environment Configuration**: Secure API key and credential management
- **Multi-user Support**: Isolated user sessions with persistent conversation storage

### 🚧 Advanced Features (In Development)
- **Mood Analysis**: Sentiment tracking and emotional pattern detection
- **Journaling Interface**: Daily thought recording with mood visualization
- **Habit Suggestions**: Personalized recommendations based on mood patterns
- **Progress Tracking**: Historical mood analytics and improvement insights

## 🏗️ Architecture

```
User Interface (Streamlit)
       ↓
Configuration Layer (Environment Variables)
       ↓
Chatbot Engine (Gemini API)
       ↓
Backend Services (Firestore)
       ↓
Data Storage (User Sessions, Conversations, Mood Data)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Project with Firestore enabled
- Google AI Studio API key (Gemini)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rith-2056/ai-mental-health-companion.git
   cd ai-mental-health-companion
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

   Required environment variables:
   ```env
   GOOGLE_API_KEY=your-gemini-api-key
   GOOGLE_CLOUD_PROJECT_ID=your-project-id
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

4. **Run the application**
   ```bash
   streamlit run src/main.py
   ```

5. **Access the app**
   Open your browser to `http://localhost:8501`

## 📁 Project Structure

```
ai-mental-health-companion/
├── src/
│   ├── main.py                 # Streamlit app entry point
│   ├── config.py              # Configuration management
│   ├── chatbot/
│   │   ├── gemini_client.py   # Gemini API integration
│   │   ├── enhanced_chatbot.py # Advanced chatbot features
│   │   └── simple_enhanced_chatbot.py
│   ├── backend/
│   │   ├── firestore_config.py # Database configuration
│   │   ├── firestore_service.py # Database operations
│   │   ├── models.py          # Data models
│   │   ├── mood_analyzer.py   # Sentiment analysis
│   │   └── habit_suggestions.py # Recommendation engine
│   └── ui/
│       ├── chat_interface.py  # Main chat UI
│       └── enhanced_chat_interface.py # Advanced UI features
├── tests/                     # Unit and integration tests
├── requirements.txt           # Python dependencies
└── .env.example              # Environment template
```

## 🔧 Configuration

### Google Cloud Setup
1. Create a Google Cloud Project
2. Enable Firestore API
3. Create a service account and download credentials
4. Set `GOOGLE_APPLICATION_CREDENTIALS` to the JSON file path

### Gemini API Setup
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Generate an API key
3. Set `GOOGLE_API_KEY` in your environment

## 🛡️ Privacy & Security

- **Data Encryption**: All sensitive data encrypted in transit and at rest
- **User Isolation**: Each user's data is completely isolated in Firestore
- **No Personal Data Storage**: No personally identifiable information stored
- **Session Management**: Secure session handling with automatic cleanup
- **HIPAA-Compliant Design**: Built with healthcare data privacy principles

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Individual test files:
```bash
python test_enhanced_chatbot.py
python test_firestore.py
python test_simple_enhanced.py
```

## 🚀 Deployment

### Local Development
```bash
streamlit run src/main.py
```

### Production Deployment
The application is designed for deployment on:
- **Google Cloud Run**: Containerized deployment
- **Google App Engine**: Managed platform deployment
- **Docker**: Container-based deployment

## 🎯 Roadmap

### Phase 1: Core Implementation ✅
- [x] Basic chatbot with Gemini integration
- [x] Firestore backend setup
- [x] Streamlit UI development
- [x] Environment configuration

### Phase 2: Advanced Features 🚧
- [ ] Mood analysis and sentiment tracking
- [ ] Journaling interface with mood widgets
- [ ] Habit suggestion engine
- [ ] Progress visualization and analytics

### Phase 3: Deployment & Scale 📋
- [ ] Docker containerization
- [ ] Cloud deployment (GCP)
- [ ] Load testing and optimization
- [ ] Comprehensive documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application is designed for educational and supportive purposes only. It is not a substitute for professional mental health care, therapy, or medical advice. If you're experiencing a mental health crisis, please contact:

- **Emergency Services**: 911 (US) or your local emergency number
- **National Suicide Prevention Lifeline**: 988 (US)
- **Crisis Text Line**: Text HOME to 741741 (US)

## 🙏 Acknowledgments

- Google AI for the Gemini API
- Google Cloud for Firestore and hosting infrastructure
- Streamlit for the rapid UI development framework
- The open-source community for inspiration and tools

---

**Built with ❤️ for mental health awareness and support**
