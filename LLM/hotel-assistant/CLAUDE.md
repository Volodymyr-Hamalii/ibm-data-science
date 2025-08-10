# CLAUDE.md

## 🧠 Project Purpose

This project is an AI-powered hotel recommendation assistant with a **conversational chat interface** built using **FastAPI**, **NextJS**, **Elasticsearch**, and a **Retrieval-Augmented Generation (RAG)** pipeline. The system features an intelligent chat bot that collects user preferences through natural conversation before providing personalized hotel recommendations.

The goal is to gain practical experience with:

- FastAPI for microservice architecture
- NextJS + TypeScript for modern frontend development
- Conversational AI for information collection
- RAG pipelines using vector embeddings and LLMs
- Elasticsearch for vector similarity search
- LangChain for orchestration
- OpenAI and Claude for language understanding/generation

---

## 🗂️ Project Structure

hotel-assistant/
├── app/
│ ├── api/ # FastAPI endpoints
│ │ └── endpoints/
│ │ ├── hotels.py # Hotel search endpoints
│ │ └── chat.py # Conversational chat endpoints
│ ├── core/ # Configs and shared clients
│ │ ├── config.py # Loads .env settings
│ │ └── es_client.py # Elasticsearch client with auth
│ ├── models/ # Pydantic models
│ │ ├── hotel.py # Hotel data models
│ │ └── chat.py # Chat conversation models
│ ├── services/ # Business logic
│ │ ├── rag_service.py # RAG flow: embed → search → return
│ │ └── chat_service.py # Conversation logic & info collection
│ └── main.py # FastAPI app entry point with CORS
├── frontend/ # NextJS chat interface
│ ├── src/
│ │ ├── app/
│ │ │ └── page.tsx # Main chat interface
│ │ └── components/
│ │ ├── ChatMessage.tsx # Chat message bubbles
│ │ └── HotelCard.tsx # Hotel recommendation cards
│ └── package.json # Frontend dependencies
├── .env # Environment variables
├── run_app.sh # Full application launcher with health checks
├── CLAUDE.md # Instructions for Claude Code
├── README_CHAT.md # Comprehensive chat system documentation
├── Dockerfile # App containerization
├── requirements.txt # Python dependencies

---

## ⚙️ Technologies & Libraries

| Layer             | Tools                                            |
| ----------------- | ------------------------------------------------ |
| Frontend UI       | NextJS 15, React, TypeScript, Tailwind CSS       |
| API Framework     | FastAPI with CORS middleware                     |
| Chat Logic        | Custom conversation service with NLP extraction  |
| Vector Store      | Elasticsearch (dense_vector + cosine similarity) |
| Embeddings        | OpenAI (`text-embedding-3-small`) or HuggingFace |
| RAG Orchestration | LangChain                                        |
| LLM Interface     | Claude (for generation), OpenAI (for embedding)  |
| Auth              | Basic Auth for Elasticsearch                     |
| Config            | `pydantic_settings` with `.env` loading          |

---

## 🔍 How the AI Assistant Works

### 💬 Conversational Flow

1. **User starts conversation** through the NextJS chat interface
2. **Chat service extracts information** from natural language (location, dates, preferences)
3. **System tracks conversation state** and missing requirements
4. **Bot asks clarifying questions** if essential information is missing (e.g., location)
5. **When ready, performs hotel search** using collected preferences
6. **Returns personalized recommendations** with visual hotel cards
7. **Maintains conversation context** for follow-up questions

### 🔧 Technical Flow

1. User message → NextJS frontend → FastAPI chat endpoint
2. Chat service processes message and extracts preferences
3. If enough info collected → RAG service performs vector search
4. Hotel results → Visual cards in frontend with context panel

---

## 🚀 Quick Start

### Single Command Launch

```bash
./run_app.sh
```

This script will:

- ✅ Check prerequisites (Python, Node.js, Elasticsearch)
- 🔍 Verify Elasticsearch connectivity and index status
- 📦 Setup Python virtual environment and install dependencies
- 🎨 Setup frontend dependencies if needed
- 🚀 Start both backend (port 8000) and frontend (port 3000)
- 🌐 Automatically open the chat interface in your browser

### Access Points

- **Chat Interface**: <http://localhost:3000> (main UI)
- **Backend API**: <http://localhost:8000>
- **API Documentation**: <http://localhost:8000/docs>

---

## 💬 Chat System Features

### 🧠 Intelligent Information Collection

The chat bot automatically extracts:

- **Location** (required) - "hotels in Paris", "near downtown"
- **Dates** - "March 15-18", "next weekend"
- **Guests** - "2 people", "family of 4"
- **Budget** - "under $200", "luxury"
- **Hotel Type** - "boutique", "business hotel"
- **Amenities** - "pool", "parking", "WiFi"

### 🎯 Conversation Intelligence

- **Context Awareness**: Remembers preferences throughout conversation
- **Smart Questioning**: Only asks for missing essential information
- **Natural Language**: Handles casual, conversational input
- **Search Triggering**: Performs search when sufficient info is available

### 🎨 User Interface

- **Real-time Chat**: Message bubbles with timestamps
- **Context Panel**: Live display of extracted preferences
- **Hotel Cards**: Visual recommendations with amenities and highlights
- **Session Management**: Clear chat and start fresh

---

## 📌 Claude Use Cases

Claude can assist with:

### 🎯 Chat System Development

- Improving natural language processing for preference extraction
- Adding new conversation flows and question patterns
- Enhancing the chat UI with additional features
- Creating more sophisticated context management
- Adding multi-language support to the chat interface

### 🏗️ Backend Development

- Writing or updating FastAPI routes and Pydantic models
- Generating custom prompt templates or summaries
- Improving or testing the RAG pipeline
- Debugging Elasticsearch queries
- Suggesting improvements to LangChain usage
- Creating new API endpoints for enhanced functionality

### 🎨 Frontend Development

- Adding new React components for the chat interface
- Improving the UI/UX of the hotel recommendation cards
- Creating mobile-responsive design improvements
- Adding animations and better user feedback
- Implementing advanced filtering and search features

### 🚀 Infrastructure & Deployment

- Writing infrastructure (e.g., Docker, IaC templates)
- Creating deployment scripts and CI/CD pipelines
- Setting up monitoring and logging for the chat system
- Optimizing performance for production use

---

## 🧪 Example Queries for Claude

### Chat System Enhancements

- "Add support for hotel price range filtering in the chat"
- "Create a feature to save user's favorite hotel searches"
- "Implement a rating system for hotel recommendations"
- "Add voice input support to the chat interface"

### Backend Improvements

- "Create a new endpoint that returns hotels grouped by country"
- "Write a test case for the `chat_service.py` conversation logic"
- "Add email notification when user finds a hotel they like"
- "Implement user authentication and chat history persistence"

### Technical Optimizations

- "Explain how to extend this to use Claude as the generator instead of OpenAI"
- "Refactor the `rag_service.py` to allow dynamic model switching"
- "Write a prompt template to generate friendly hotel summaries"
- "Add caching to improve chat response times"

---

## 🔧 Development Commands

### Quick Start

```bash
./run_app.sh  # Starts everything with health checks
```

### Manual Development

```bash
# Backend only (Terminal 1)
cd app && python -m uvicorn main:app --reload --port 8000

# Frontend only (Terminal 2)
cd frontend && npm run dev

# Check Elasticsearch
curl http://localhost:9200/_cluster/health
```

---

## ✅ Environment Variables (.env)

```env
# Elasticsearch Configuration
ES_URL=http://localhost:9200
ES_INDEX=hotels

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Claude Configuration (for future LLM integration)
# ANTHROPIC_API_KEY=your_claude_api_key_here
```

---

## 📚 Additional Resources

- **README_CHAT.md** - Comprehensive chat system documentation
- **Frontend Code** - Located in `frontend/src/`
- **API Documentation** - Available at <http://localhost:8000/docs> when running
- **Chat API Endpoints** - `/api/chat/*` for conversation management
- **Hotel API Endpoints** - `/api/recommendations` for direct hotel search
