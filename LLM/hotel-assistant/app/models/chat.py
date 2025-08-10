from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[str] = None

class UserContext(BaseModel):
    """Store user preferences and collected information throughout conversation"""
    location: Optional[str] = None
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None
    guests: Optional[int] = None
    budget_range: Optional[str] = None
    preferred_amenities: List[str] = []
    hotel_type: Optional[str] = None
    special_requirements: List[str] = []

class ConversationState(BaseModel):
    """Track the current state of conversation and what info we still need"""
    session_id: str
    messages: List[ChatMessage] = []
    user_context: UserContext = UserContext()
    missing_info: List[str] = []
    ready_to_search: bool = False
    last_query: Optional[str] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    message: str
    user_context: UserContext
    missing_info: List[str]
    ready_to_search: bool
    suggested_hotels: Optional[List[Dict[str, Any]]] = None