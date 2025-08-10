'use client';

import { useState, useRef, useEffect } from 'react';
import ChatMessage from '@/components/ChatMessage';
import HotelCard from '@/components/HotelCard';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface UserContext {
  location?: string;
  check_in_date?: string;
  check_out_date?: string;
  guests?: number;
  budget_range?: string;
  preferred_amenities: string[];
  hotel_type?: string;
  special_requirements: string[];
}

interface Hotel {
  id: string;
  title: string;
  description: string;
  amenities: Record<string, string[]>;
  location: { lat: number; lon: number };
  highlights: string[];
  local_tips: string[];
  url: string;
}

interface ChatResponse {
  session_id: string;
  message: string;
  user_context: UserContext;
  missing_info: string[];
  ready_to_search: boolean;
  suggested_hotels?: Hotel[];
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hi! I\'m your hotel assistant. I can help you find the perfect hotel for your stay. Just tell me what you\'re looking for!',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [userContext, setUserContext] = useState<UserContext>({
    preferred_amenities: [],
    special_requirements: []
  });
  const [suggestedHotels, setSuggestedHotels] = useState<Hotel[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Create a new session when component mounts
    fetch('http://localhost:8000/api/chat/new-session', {
      method: 'POST'
    })
      .then(res => res.json())
      .then(data => setSessionId(data.session_id))
      .catch(err => console.error('Failed to create session:', err));
  }, []);

  const sendMessage = async () => {
    if (!input.trim() || !sessionId) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: input
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data: ChatResponse = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.message,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setUserContext(data.user_context);
      
      if (data.suggested_hotels) {
        setSuggestedHotels(data.suggested_hotels);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = async () => {
    if (!sessionId) return;
    
    try {
      await fetch(`http://localhost:8000/api/chat/${sessionId}`, {
        method: 'DELETE'
      });
      
      // Reset state
      setMessages([{
        role: 'assistant',
        content: 'Hi! I\'m your hotel assistant. I can help you find the perfect hotel for your stay. Just tell me what you\'re looking for!',
        timestamp: new Date().toISOString()
      }]);
      setUserContext({ preferred_amenities: [], special_requirements: [] });
      setSuggestedHotels([]);
      
      // Create new session
      const response = await fetch('http://localhost:8000/api/chat/new-session', {
        method: 'POST'
      });
      const data = await response.json();
      setSessionId(data.session_id);
      
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🏨 Hotel Assistant
          </h1>
          <p className="text-gray-600">
            Find your perfect hotel with AI-powered recommendations
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Chat Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-xl h-[600px] flex flex-col">
              {/* Chat Header */}
              <div className="p-4 border-b border-gray-200 flex justify-between items-center">
                <h2 className="font-semibold text-gray-800">Chat</h2>
                <button
                  onClick={clearChat}
                  className="text-sm text-gray-500 hover:text-red-500 transition-colors"
                >
                  Clear Chat
                </button>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message, index) => (
                  <ChatMessage key={index} message={message} />
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-lg p-3">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-4 border-t border-gray-200">
                <div className="flex space-x-2">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Tell me about your ideal hotel..."
                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    rows={1}
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={isLoading || !input.trim()}
                    className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Context Panel */}
          <div className="space-y-6">
            {/* User Context */}
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h3 className="font-semibold text-gray-800 mb-4">Your Preferences</h3>
              <div className="space-y-3 text-sm">
                {userContext.location && (
                  <div className="flex items-center space-x-2">
                    <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                    <span><strong>Location:</strong> {userContext.location}</span>
                  </div>
                )}
                {userContext.check_in_date && (
                  <div className="flex items-center space-x-2">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    <span><strong>Check-in:</strong> {userContext.check_in_date}</span>
                  </div>
                )}
                {userContext.check_out_date && (
                  <div className="flex items-center space-x-2">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    <span><strong>Check-out:</strong> {userContext.check_out_date}</span>
                  </div>
                )}
                {userContext.guests && (
                  <div className="flex items-center space-x-2">
                    <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                    <span><strong>Guests:</strong> {userContext.guests}</span>
                  </div>
                )}
                {userContext.budget_range && (
                  <div className="flex items-center space-x-2">
                    <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                    <span><strong>Budget:</strong> {userContext.budget_range}</span>
                  </div>
                )}
                {userContext.hotel_type && (
                  <div className="flex items-center space-x-2">
                    <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
                    <span><strong>Type:</strong> {userContext.hotel_type}</span>
                  </div>
                )}
                {userContext.preferred_amenities.length > 0 && (
                  <div className="flex items-start space-x-2">
                    <span className="w-2 h-2 bg-pink-500 rounded-full mt-1"></span>
                    <div>
                      <strong>Amenities:</strong>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {userContext.preferred_amenities.map((amenity, index) => (
                          <span key={index} className="bg-gray-100 px-2 py-1 rounded text-xs">
                            {amenity}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Hotel Results */}
            {suggestedHotels.length > 0 && (
              <div className="bg-white rounded-2xl shadow-xl p-6">
                <h3 className="font-semibold text-gray-800 mb-4">Suggested Hotels</h3>
                <div className="space-y-4">
                  {suggestedHotels.map((hotel, index) => (
                    <HotelCard key={hotel.id} hotel={hotel} />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
