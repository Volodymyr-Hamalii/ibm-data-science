# 💬 Hotel Assistant Chat System

A user-friendly conversational interface for hotel recommendations that intelligently collects user preferences before performing searches.

## 🚀 Quick Start

### Option 1: Use the startup script (recommended)
```bash
./start_dev.sh
```

### Option 2: Manual startup
```bash
# Backend (Terminal 1)
cd app
python -m uvicorn main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 Features

### Intelligent Conversation Flow
- **Context Awareness**: Remembers user preferences throughout the conversation
- **Information Collection**: Asks for missing details (location, dates, guests, budget)
- **Natural Language Processing**: Extracts hotel preferences from natural language
- **Smart Search Triggering**: Only searches when sufficient information is available

### User-Friendly Interface
- **Real-time Chat**: Responsive chat interface with typing indicators
- **Context Panel**: Live display of collected preferences
- **Hotel Cards**: Visual hotel recommendations with key details
- **Session Management**: Clear chat and start fresh conversations

### Extracted Information
The system intelligently extracts:
- **Location** (required)
- **Check-in/Check-out dates**
- **Number of guests**
- **Budget range**
- **Hotel type** (luxury, budget, boutique, etc.)
- **Amenities** (pool, WiFi, parking, etc.)
- **Special requirements**

## 💡 Example Conversations

### Scenario 1: Missing Location
```
User: "I need a hotel with a pool"
Bot: "I'd be happy to help you find hotels! Could you tell me which city or area you're looking to stay in?"
User: "New York"
Bot: "Great! I can help you find hotels in New York. To give you the best recommendations, could you share your travel dates and how many guests will be staying?"
```

### Scenario 2: Complete Information
```
User: "I need a luxury hotel in Paris for 2 guests from March 15-18 with spa and restaurant"
Bot: "Great! I found some excellent hotels in Paris for you: [shows hotel recommendations]"
```

### Scenario 3: Gradual Information Building
```
User: "Looking for a place to stay"
Bot: "I'd be happy to help you find hotels! Could you tell me which city or area you're looking to stay in?"
User: "London, something budget-friendly"
Bot: "Perfect! I'll help you find budget-friendly hotels in London. What are your check-in and check-out dates?"
User: "Next weekend, just me"
Bot: "Thanks for the details! Let me search for budget-friendly hotels in London that match your preferences."
```

## 🏗️ Architecture

### Backend Components
```
app/
├── api/endpoints/
│   ├── chat.py          # Chat endpoints
│   └── hotels.py        # Hotel search endpoints
├── models/
│   ├── chat.py          # Chat data models
│   └── hotel.py         # Hotel data models
├── services/
│   ├── chat_service.py  # Conversation logic
│   └── rag_service.py   # Hotel search logic
└── main.py              # FastAPI app with CORS
```

### Frontend Components
```
frontend/src/
├── app/
│   └── page.tsx         # Main chat interface
└── components/
    ├── ChatMessage.tsx  # Individual chat messages
    └── HotelCard.tsx    # Hotel recommendation cards
```

## 🔧 API Endpoints

### Chat Endpoints
- `POST /api/chat/chat` - Send chat message
- `POST /api/chat/new-session` - Create new chat session
- `GET /api/chat/{session_id}/history` - Get conversation history
- `DELETE /api/chat/{session_id}` - Clear conversation

### Hotel Endpoints
- `GET /api/recommendations` - Direct hotel search (legacy)
- `GET /api/debug/elasticsearch` - Debug Elasticsearch connection
- `GET /api/debug/test-search` - Test search functionality

## 🧠 Conversation Logic

### Information Extraction
The chat service uses pattern matching to extract:
- **Location patterns**: "in Paris", "near London", "Manhattan hotel"
- **Date patterns**: "March 15-18", "next weekend", "12/25/2024"
- **Guest patterns**: "2 guests", "family of 4", "solo traveler"
- **Budget patterns**: "under $200", "budget-friendly", "luxury"
- **Amenity keywords**: "pool", "WiFi", "parking", "breakfast"

### Decision Flow
1. **Extract information** from user message
2. **Update user context** with new information
3. **Check for missing required info** (primarily location)
4. **Determine if ready to search** (location + optional details)
5. **Generate appropriate response**:
   - Ask clarifying questions if info missing
   - Perform hotel search if ready
   - Provide recommendations with context

## 🎨 UI Features

### Chat Interface
- **Message bubbles** with timestamps
- **Typing indicators** during processing
- **Auto-scroll** to latest message
- **Enter to send** keyboard shortcut

### Context Panel
- **Live preference tracking** with colored indicators
- **Amenity tags** for easy viewing
- **Clear visual hierarchy**

### Hotel Results
- **Compact hotel cards** with key information
- **Highlight tags** for important features
- **Amenity badges** for quick scanning
- **Location coordinates** for reference

## 🔄 Session Management

- **Unique session IDs** for each conversation
- **In-memory storage** (development) - easily upgradeable to Redis/database
- **Session persistence** throughout conversation
- **Clean slate** with clear chat functionality

## 🚀 Future Enhancements

- **LLM Integration**: Use Claude/GPT for more natural responses
- **Persistent Storage**: Database for conversation history
- **User Accounts**: Save preferences across sessions
- **Advanced Filters**: More sophisticated search criteria
- **Map Integration**: Visual hotel locations
- **Booking Integration**: Direct reservation capabilities
- **Multi-language Support**: International accessibility