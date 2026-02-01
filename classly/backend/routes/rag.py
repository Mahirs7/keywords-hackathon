"""
RAG (Retrieval-Augmented Generation) Routes for Course Q&A
Provides endpoints for asking questions about course materials using vector search.
"""

from flask import Blueprint, jsonify, request
import os
import hashlib
from typing import List, Dict, Any, Optional

from supabase import create_client, Client

# Initialize blueprint
rag_bp = Blueprint('rag', __name__)

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

EMBEDDING_DIM = 1536

# Initialize Supabase client
_supabase_client = None

def get_supabase() -> Client:
    """Get or create Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Missing Supabase credentials")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


# ============================================
# Embedding Functions
# ============================================

def create_deterministic_embedding(text: str) -> List[float]:
    """
    Create a deterministic fake embedding based on text hash.
    Used when OpenAI API key is not available.
    """
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    
    embedding = []
    for i in range(EMBEDDING_DIM):
        hex_chunk = text_hash[(i * 4) % len(text_hash):((i * 4) % len(text_hash)) + 4]
        if len(hex_chunk) < 4:
            hex_chunk = text_hash[:4]
        val = (int(hex_chunk, 16) / 65535) * 2 - 1
        embedding.append(val)
    
    # Normalize
    magnitude = sum(x ** 2 for x in embedding) ** 0.5
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]
    
    return embedding


def create_openai_embedding(text: str) -> List[float]:
    """Create embedding using OpenAI API."""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding


def get_query_embedding(text: str) -> List[float]:
    """Get embedding for query text."""
    if OPENAI_API_KEY:
        try:
            return create_openai_embedding(text)
        except Exception as e:
            print(f"OpenAI embedding failed: {e}, using deterministic")
    return create_deterministic_embedding(text)


# ============================================
# LLM Functions
# ============================================

def generate_answer_with_openai(question: str, context_chunks: List[Dict], course_code: str) -> str:
    """Generate an answer using OpenAI ChatCompletion."""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Build context from chunks
    context_text = "\n\n---\n\n".join([
        f"[Source: {chunk.get('metadata', {}).get('doc_title', 'Unknown')}]\n{chunk['content']}"
        for chunk in context_chunks
    ])
    
    system_prompt = f"""You are a helpful teaching assistant for {course_code}. 
Answer the student's question based ONLY on the provided course materials.
If the information isn't in the provided context, say so clearly.
Be concise but thorough. Cite specific sources when relevant."""

    user_prompt = f"""Course Materials:
{context_text}

Student Question: {question}

Answer based on the course materials above:"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return response.choices[0].message.content


def generate_mock_answer(question: str, context_chunks: List[Dict], course_code: str) -> str:
    """Generate a synthesized answer from chunks without using LLM."""
    if not context_chunks:
        return f"I couldn't find relevant information about that in the {course_code} course materials."
    
    # Extract key information from chunks
    relevant_info = []
    for chunk in context_chunks[:3]:  # Use top 3 chunks
        content = chunk['content'][:300]  # First 300 chars
        source = chunk.get('metadata', {}).get('doc_title', 'course materials')
        relevant_info.append(f"From {source}: {content}...")
    
    answer = f"Based on the {course_code} course materials:\n\n"
    answer += "\n\n".join(relevant_info)
    answer += "\n\n(Note: This is a summarized response. Enable OPENAI_API_KEY for AI-generated answers.)"
    
    return answer


def generate_answer(question: str, context_chunks: List[Dict], course_code: str) -> str:
    """Generate an answer using available method."""
    if OPENAI_API_KEY:
        try:
            return generate_answer_with_openai(question, context_chunks, course_code)
        except Exception as e:
            print(f"OpenAI generation failed: {e}")
    return generate_mock_answer(question, context_chunks, course_code)


# ============================================
# Routes
# ============================================

@rag_bp.route('/courses', methods=['GET'])
def get_courses():
    """Get all available courses for RAG Q&A."""
    try:
        supabase = get_supabase()
        result = supabase.table('classes').select('id, code, title').order('code').execute()
        
        return jsonify({
            'success': True,
            'courses': result.data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@rag_bp.route('/ask', methods=['POST'])
def ask_question():
    """
    Ask a question about courses using RAG.
    
    Request body:
    {
        "courseCodes": ["CS225", "CS374"],  // empty array = search all courses
        "question": "What are the upcoming assignments?"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No JSON body provided'}), 400
        
        course_codes = data.get('courseCodes', [])  # Empty = all courses
        question = data.get('question')
        
        if not question:
            return jsonify({'success': False, 'error': 'question is required'}), 400
        
        supabase = get_supabase()
        
        # Step 1: Get course IDs to search
        all_course_ids = []
        course_names = []
        
        if course_codes and len(course_codes) > 0:
            # Search specific courses
            for code in course_codes:
                course_result = supabase.table('classes').select('id, code, title').eq('code', code).execute()
                if course_result.data:
                    all_course_ids.append(course_result.data[0]['id'])
                    course_names.append(course_result.data[0]['title'])
        else:
            # Search ALL courses
            all_courses = supabase.table('classes').select('id, code, title').execute()
            for c in all_courses.data:
                all_course_ids.append(c['id'])
                course_names.append(c['title'])
        
        if not all_course_ids:
            return jsonify({
                'success': False,
                'error': 'No courses found'
            }), 404
        
        # Fetch actual course data to include in context
        course_data_context = []
        
        # Get deadlines/assignments for selected courses
        for i, course_id in enumerate(all_course_ids):
            course_code = course_codes[i] if course_codes and i < len(course_codes) else 'Unknown'
            course_name = course_names[i] if i < len(course_names) else 'Unknown'
            
            # Get deadlines for this course
            deadlines_result = supabase.table('deadlines').select('*').eq('course_name', course_name).order('due_date').limit(20).execute()
            
            if deadlines_result.data:
                course_data_context.append(f"\n## {course_code} - {course_name} Assignments:")
                for d in deadlines_result.data:
                    due = d.get('due_date_text') or d.get('due_date') or 'No due date'
                    status = d.get('status', 'pending')
                    points = d.get('points_possible', '')
                    dtype = d.get('type', 'assignment')
                    course_data_context.append(f"- {d['title']} ({dtype}): Due {due}, Status: {status}" + (f", Points: {points}" if points else ""))
        
        # Build context string
        context_str = "\n".join(course_data_context) if course_data_context else "No assignment data available for these courses yet."
        
        # Generate answer using OpenAI with actual course data
        courses_str = ', '.join(course_codes) if course_codes else 'all your courses'
        courses_names_str = ', '.join(course_names) if course_names else 'your courses'
        
        if OPENAI_API_KEY:
            try:
                import requests
                
                system_prompt = f"""You are a helpful teaching assistant for: {courses_names_str}.
You have access to the student's actual course data below. Use this information to answer their questions accurately.

COURSE DATA:
{context_str}

Answer the student's question based on this data. Be specific and reference actual assignments, due dates, etc. when relevant.
If the data doesn't contain what they're asking about, let them know what information IS available."""

                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {OPENAI_API_KEY}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'gpt-4o',
                        'messages': [
                            {'role': 'system', 'content': system_prompt},
                            {'role': 'user', 'content': question}
                        ],
                        'temperature': 0.3,
                        'max_tokens': 500
                    }
                )
                
                if response.status_code == 200:
                    answer = response.json()['choices'][0]['message']['content']
                else:
                    error_detail = response.json().get('error', {}).get('message', response.status_code)
                    answer = f"I can help you with questions about {courses_str}. (API Error: {error_detail})"
            except Exception as e:
                answer = f"I can help you with questions about {courses_str}. (Error: {str(e)})"
        else:
            answer = f"I can help you with questions about {courses_str}. Configure OPENAI_API_KEY for AI-powered answers."
        
        # Format response
        return jsonify({
            'success': True,
            'courseCodes': course_codes if course_codes else ['all'],
            'courseNames': course_names,
            'question': question,
            'answer': answer,
            'sources': [],
            'retrieved': [],
            'metadata': {
                'llm_type': 'openai' if OPENAI_API_KEY else 'mock'
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@rag_bp.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for the Study Buddy chatbot.

    Request body (JSON):
      - message (str, required): The user's message or question.
      - course_context (str, optional): A short description of the relevant course
        or classes to help tailor the response (e.g. course name, code, topic).

    Behavior:
      - If `message` is empty or missing, the endpoint returns a JSON object with
        a simple prompt asking the user to send a message.
      - If `OPENAI_API_KEY` is configured, the endpoint may call the OpenAI Chat
        Completions API using an internal system prompt that describes the "Study
        Buddy" assistant and the provided course context.
      - If `OPENAI_API_KEY` is not configured, the endpoint falls back to a simple
        non-LLM response and does not make any external OpenAI API calls.

    Response:
      - Returns a JSON object with at least:
          * response (str): The chatbot's reply to the user.
        Additional metadata fields may be included to describe how the response
        was generated.
    """
    try:
        data = request.json or {}
        message = data.get('message', '')
        course_context = data.get('course_context', '')
        
        if not message:
            return jsonify({'response': 'Please send a message!'})
        
        # Build system prompt
        system_prompt = f"""You are a helpful study assistant called "Study Buddy" for a college student.
You're helping them with their course: {course_context if course_context else 'their classes'}.
Be friendly, encouraging, and concise. Use emojis occasionally.
If asked about due dates, remind them to check their assignments page for the latest info.
Keep responses under 150 words unless they ask for detailed explanations."""

        if OPENAI_API_KEY:
            try:
                import requests as http_requests
                response = http_requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message}
                        ],
                        "max_tokens": 300,
                        "temperature": 0.7
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    answer = response.json()['choices'][0]['message']['content']
                    return jsonify({'response': answer})
                else:
                    return jsonify({'response': f"I'm having trouble thinking right now. Try again in a moment! 🤔"})
            except Exception as e:
                print(f"Chat error: {e}")
                return jsonify({'response': "Oops! Something went wrong. Let me try again... 🔄"})
        else:
            # Mock response when no API key
            responses = [
                f"Great question about {course_context}! 📚 I'd love to help, but my AI brain needs an API key to give you detailed answers.",
                f"I'm your study buddy for {course_context}! For now, check your assignments page for due dates.",
                "Let's study together! 🎯 What topic should we focus on?",
            ]
            import random
            return jsonify({'response': random.choice(responses)})
            
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        return jsonify({'response': "Sorry, I encountered an error. Please try again!"})


@rag_bp.route('/health', methods=['GET'])
def health_check():
    """Check RAG service health and configuration."""
    try:
        supabase = get_supabase()
        
        # Check if tables exist by querying
        courses = supabase.table('rag_courses').select('id').limit(1).execute()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'config': {
                'supabase_connected': True,
                'openai_available': bool(OPENAI_API_KEY),
                'embedding_type': 'openai' if OPENAI_API_KEY else 'deterministic',
                'llm_type': 'openai' if OPENAI_API_KEY else 'mock'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500
