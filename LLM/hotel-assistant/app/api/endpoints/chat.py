from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service
import uuid

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_message(request: ChatRequest) -> ChatResponse:
    """Process a chat message and return response with context"""
    try:
        response = chat_service.process_message(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")

@router.post("/chat/new-session")
async def create_chat_session():
    """Create a new chat session ID"""
    return {"session_id": str(uuid.uuid4())}

@router.get("/chat/{session_id}/history")
async def get_chat_history(session_id: str):
    """Get conversation history for a session"""
    history = chat_service.get_conversation_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    return history

@router.delete("/chat/{session_id}")
async def clear_chat_session(session_id: str):
    """Clear conversation history for a session"""
    success = chat_service.clear_conversation(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session cleared successfully"}