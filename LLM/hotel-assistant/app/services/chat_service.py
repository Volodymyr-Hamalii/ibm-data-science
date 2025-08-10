from typing import Dict, List, Optional
import uuid
import re
from datetime import datetime
from app.models.chat import (
    ConversationState, ChatMessage, MessageRole, UserContext, 
    ChatRequest, ChatResponse
)
from app.services.rag_service import recommend_hotels
from app.models.hotel import Hotel

# In-memory storage for conversation states (in production, use Redis or database)
conversation_storage: Dict[str, ConversationState] = {}

class ChatService:
    def __init__(self):
        self.required_info = ["location"]  # Minimum required info for search
        self.optional_info = ["check_in_date", "check_out_date", "guests", "budget_range", "hotel_type"]
    
    def _extract_user_info(self, message: str, current_context: UserContext) -> UserContext:
        """Extract hotel-related information from user message"""
        message_lower = message.lower()
        updated_context = current_context.copy()
        
        # Extract location
        location_patterns = [
            r"in\s+([a-zA-Z\s]+?)(?:\s|$|,)",
            r"(?:near|at|around)\s+([a-zA-Z\s]+?)(?:\s|$|,)",
            r"([a-zA-Z\s]+?)\s+(?:hotel|resort|accommodation)",
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, message_lower)
            if match:
                location = match.group(1).strip()
                if len(location) > 2 and location not in ["the", "a", "an", "hotel", "resort"]:
                    updated_context.location = location.title()
                    break
        
        # Extract dates
        date_patterns = [
            r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
            r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}",
        ]
        
        dates_found = []
        for pattern in date_patterns:
            dates_found.extend(re.findall(pattern, message_lower))
        
        if len(dates_found) >= 2:
            updated_context.check_in_date = dates_found[0]
            updated_context.check_out_date = dates_found[1]
        elif len(dates_found) == 1:
            if not updated_context.check_in_date:
                updated_context.check_in_date = dates_found[0]
        
        # Extract number of guests
        guest_match = re.search(r"(\d+)\s+(?:guest|person|people|adult)", message_lower)
        if guest_match:
            updated_context.guests = int(guest_match.group(1))
        
        # Extract budget
        budget_patterns = [
            r"under\s+\$?(\d+)",
            r"less\s+than\s+\$?(\d+)",
            r"budget\s+of\s+\$?(\d+)",
            r"around\s+\$?(\d+)",
            r"\$(\d+)",
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, message_lower)
            if match:
                amount = int(match.group(1))
                if amount < 100:
                    updated_context.budget_range = f"Under ${amount}"
                elif amount < 200:
                    updated_context.budget_range = f"${amount-50}-${amount+50}"
                else:
                    updated_context.budget_range = f"Around ${amount}"
                break
        
        # Extract amenities
        amenity_keywords = {
            "pool": "pool",
            "swimming": "pool", 
            "wifi": "wifi",
            "internet": "wifi",
            "parking": "parking",
            "breakfast": "breakfast",
            "gym": "fitness",
            "fitness": "fitness",
            "spa": "spa",
            "beach": "beach access",
            "restaurant": "restaurant",
            "bar": "bar",
            "pet": "pet-friendly"
        }
        
        for keyword, amenity in amenity_keywords.items():
            if keyword in message_lower and amenity not in updated_context.preferred_amenities:
                updated_context.preferred_amenities.append(amenity)
        
        # Extract hotel type
        type_keywords = {
            "luxury": "luxury",
            "budget": "budget",
            "boutique": "boutique",
            "resort": "resort",
            "business": "business",
            "family": "family-friendly",
            "romantic": "romantic",
        }
        
        for keyword, hotel_type in type_keywords.items():
            if keyword in message_lower:
                updated_context.hotel_type = hotel_type
                break
        
        return updated_context
    
    def _determine_missing_info(self, context: UserContext) -> List[str]:
        """Determine what information is still needed"""
        missing = []
        
        if not context.location:
            missing.append("location")
        
        # Optional but helpful info
        if not context.check_in_date:
            missing.append("check_in_date")
        if not context.check_out_date:
            missing.append("check_out_date")
        if not context.guests:
            missing.append("guests")
        
        return missing
    
    def _generate_clarifying_question(self, missing_info: List[str], context: UserContext) -> str:
        """Generate a natural question to gather missing information"""
        
        if "location" in missing_info:
            return "I'd be happy to help you find hotels! Could you tell me which city or area you're looking to stay in?"
        
        optional_missing = [info for info in missing_info if info != "location"]
        
        if len(optional_missing) >= 3:
            return f"Great! I can help you find hotels in {context.location}. To give you the best recommendations, could you share your travel dates and how many guests will be staying?"
        elif "check_in_date" in optional_missing and "check_out_date" in optional_missing:
            return f"Perfect! I'll help you find hotels in {context.location}. What are your check-in and check-out dates?"
        elif "guests" in optional_missing:
            return f"Excellent! For hotels in {context.location}, how many guests will be staying?"
        
        return f"Thanks for the details! Let me search for hotels in {context.location} that match your preferences."
    
    def _should_search_now(self, context: UserContext, missing_info: List[str]) -> bool:
        """Determine if we have enough info to perform a search"""
        # Must have location, everything else is optional but we'll ask for basics
        return bool(context.location) and len(missing_info) <= 2
    
    def _build_search_query(self, context: UserContext) -> str:
        """Build a search query from collected context"""
        query_parts = []
        
        if context.location:
            query_parts.append(f"hotel in {context.location}")
        
        if context.hotel_type:
            query_parts.append(context.hotel_type)
        
        if context.preferred_amenities:
            query_parts.append(f"with {', '.join(context.preferred_amenities)}")
        
        if context.budget_range:
            query_parts.append(f"budget {context.budget_range}")
        
        if context.guests:
            query_parts.append(f"for {context.guests} guests")
        
        return " ".join(query_parts)
    
    def process_message(self, request: ChatRequest) -> ChatResponse:
        """Main method to process user messages and manage conversation flow"""
        
        # Get or create conversation state
        if request.session_id not in conversation_storage:
            conversation_storage[request.session_id] = ConversationState(
                session_id=request.session_id
            )
        
        state = conversation_storage[request.session_id]
        
        # Add user message to conversation
        user_message = ChatMessage(
            role=MessageRole.USER,
            content=request.message,
            timestamp=datetime.now().isoformat()
        )
        state.messages.append(user_message)
        
        # Extract information from the message
        updated_context = self._extract_user_info(request.message, state.user_context)
        state.user_context = updated_context
        
        # Determine what info is still missing
        missing_info = self._determine_missing_info(updated_context)
        state.missing_info = missing_info
        
        # Decide if we should search or ask for more info
        should_search = self._should_search_now(updated_context, missing_info)
        state.ready_to_search = should_search
        
        response_message = ""
        suggested_hotels = None
        
        if should_search:
            # Build search query and get recommendations
            search_query = self._build_search_query(updated_context)
            state.last_query = search_query
            
            hotels = recommend_hotels(search_query, top_k=3)
            
            if hotels:
                response_message = f"Great! I found some excellent hotels in {updated_context.location} for you:\n\n"
                suggested_hotels = []
                
                for i, hotel in enumerate(hotels, 1):
                    response_message += f"{i}. **{hotel.title}**\n"
                    if hotel.description:
                        # Truncate description if too long
                        desc = hotel.description[:200] + "..." if len(hotel.description) > 200 else hotel.description
                        response_message += f"   {desc}\n"
                    
                    if hotel.highlights:
                        response_message += f"   • Highlights: {', '.join(hotel.highlights[:3])}\n"
                    
                    response_message += f"   • Location: {hotel.location.lat:.4f}, {hotel.location.lon:.4f}\n"
                    response_message += "\n"
                    
                    # Convert hotel to dict for response
                    suggested_hotels.append({
                        "id": hotel.id,
                        "title": hotel.title,
                        "description": hotel.description,
                        "amenities": hotel.amenities,
                        "location": {"lat": hotel.location.lat, "lon": hotel.location.lon},
                        "highlights": hotel.highlights,
                        "local_tips": hotel.local_tips,
                        "url": hotel.url
                    })
                
                response_message += "Would you like more details about any of these hotels, or would you like me to search with different criteria?"
            else:
                response_message = f"I couldn't find any hotels matching your criteria in {updated_context.location}. Could you try a different location or adjust your requirements?"
        
        else:
            # Ask for missing information
            response_message = self._generate_clarifying_question(missing_info, updated_context)
        
        # Add assistant message to conversation
        assistant_message = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=response_message,
            timestamp=datetime.now().isoformat()
        )
        state.messages.append(assistant_message)
        
        # Update storage
        conversation_storage[request.session_id] = state
        
        return ChatResponse(
            session_id=request.session_id,
            message=response_message,
            user_context=updated_context,
            missing_info=missing_info,
            ready_to_search=should_search,
            suggested_hotels=suggested_hotels
        )
    
    def get_conversation_history(self, session_id: str) -> Optional[ConversationState]:
        """Get conversation history for a session"""
        return conversation_storage.get(session_id)
    
    def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        if session_id in conversation_storage:
            del conversation_storage[session_id]
            return True
        return False

# Global instance
chat_service = ChatService()