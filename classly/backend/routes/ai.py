"""
AI API Routes
Handles chat requests and agent interactions
"""

import os
from flask import Blueprint, jsonify, request
from services.ai_agent import get_agent
from utils.auth_helpers import get_user_id_from_request
from langchain_core.messages import HumanMessage, AIMessage

ai_bp = Blueprint('ai', __name__)

# Store conversation history per user (in-memory for now)
# In production, you might want to store this in a database
_conversation_history = {}


@ai_bp.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint that processes user messages through the AI agent"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        user_message = data['message']
        # Get user_id from JWT token (Supabase Auth) or request body
        user_id = get_user_id_from_request() or data.get('user_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "Authentication required. Please log in to use the AI assistant."
            }), 401
        
        # Get or initialize conversation history for this user
        if user_id not in _conversation_history:
            _conversation_history[user_id] = []
        
        chat_history = _conversation_history[user_id]
        
        # Get agent instance for this user
        agent = get_agent(user_id)
        
        # Run agent with user message and conversation history
        # The agent will use chat_history for context and handle the current input separately
        result = agent.invoke({
            "input": user_message,
            "chat_history": chat_history  # Pass existing conversation history
        })
        
        # Get AI response
        response_text = result.get('output', 'I apologize, but I encountered an error processing your request.')
        
        # Update conversation history with new messages
        # Add user message
        chat_history.append(HumanMessage(content=user_message))
        # Add AI response
        chat_history.append(AIMessage(content=response_text))
        
        # Keep only last 20 messages to prevent memory issues
        if len(chat_history) > 20:
            _conversation_history[user_id] = chat_history[-20:]
        
        # Include intermediate steps for debugging (shows tool calls)
        intermediate_steps = result.get('intermediate_steps', [])
        tool_calls_made = len(intermediate_steps) > 0
        
        response_data = {
            "success": True,
            "response": response_text
        }
        
        # Optionally include tool call info in development
        if os.getenv('FLASK_DEBUG') == '1':
            response_data["debug"] = {
                "tool_calls_made": tool_calls_made,
                "num_tool_calls": len(intermediate_steps)
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in AI chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": str(e),
            "response": "I apologize, but I encountered an error. Please try again or check the server logs."
        }), 500


@ai_bp.route('/chat/clear', methods=['POST'])
def clear_chat_history():
    """Clear conversation history for the current user"""
    try:
        user_id = get_user_id_from_request()
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "Authentication required"
            }), 401
        
        if user_id in _conversation_history:
            _conversation_history[user_id] = []
        
        return jsonify({
            "success": True,
            "message": "Chat history cleared"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@ai_bp.route('/health', methods=['GET'])
def health():
    """Check AI agent health status"""
    try:
        from services.keywords_ai import keywords_ai_service
        from services.supabase_service import supabase_service
        from services.calendar_service import calendar_service
        
        status = {
            "keywords_ai_configured": keywords_ai_service.is_configured(),
            "supabase_configured": supabase_service.is_configured(),
            "calendar_configured": calendar_service.is_configured(),
            "agent_ready": True
        }
        
        return jsonify({
            "success": True,
            "status": status
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

