# Implementation Changelog

This document tracks all changes made during the AI Agent implementation with Keywords AI integration.

---

## [2026-01-31] - Initial Setup and Changelog Creation

### Created
- `CHANGELOG.md` - Change tracking document to monitor all implementation progress

### Notes
- Starting implementation of AI Agent feature with Keywords AI integration
- Plan includes: GPT-like chat interface, LangChain agent, Google Calendar integration, Supabase integration

---

## [2026-01-31] - Added AI Tab to Sidebar

### Modified
- `classly/app/components/Sidebar.tsx` - Added "AI" tab to navigation items with Bot icon from lucide-react

### Notes
- AI tab now appears in the main navigation section alongside Dashboard and Schedule
- Uses Bot icon for visual consistency

---

## [2026-01-31] - Created AI Chat Interface Page

### Created
- `classly/app/ai/page.tsx` - GPT-like chat interface with message history, input field, and loading states

### Features
- Message history display with user and assistant messages
- Real-time chat input with Enter key support
- Loading indicators during API calls
- Auto-scroll to latest message
- Error handling for API failures
- Styled with dark theme matching the app design

### Notes
- Frontend is ready and will connect to `/api/ai/chat` endpoint once backend is implemented
- Uses mock user data for user avatar display

---

## [2026-01-31] - Added Backend Dependencies and Services

### Modified
- `classly/backend/requirements.txt` - Added LangChain, OpenAI, and Google Calendar API dependencies

### Created
- `classly/backend/services/keywords_ai.py` - Keywords AI Gateway service for LLM calls
- `classly/backend/services/supabase_service.py` - Supabase service for fetching assignments
- `classly/backend/services/calendar_service.py` - Google Calendar service for creating events

### Features
- **Keywords AI Service**: OpenAI-compatible client for Keywords AI Gateway with chat completion support
- **Supabase Service**: Functions to fetch assignments and pending assignments (with mock fallback)
- **Calendar Service**: Create calendar events with mock mode for development

### Notes
- All services include mock/fallback modes for development without full configuration
- Services use singleton pattern for easy access throughout the application
- Environment variables needed: KEYWORDS_AI_API_KEY, SUPABASE_URL, SUPABASE_KEY, GOOGLE_CALENDAR_CLIENT_ID, GOOGLE_CALENDAR_CLIENT_SECRET

---

## [2026-01-31] - Created AI Agent and API Routes

### Created
- `classly/backend/services/ai_agent.py` - LangChain agent with tools for assignments and calendar
- `classly/backend/routes/ai.py` - API routes for AI chat endpoint

### Modified
- `classly/backend/app.py` - Registered AI blueprint and added to API endpoints list

### Features
- **AI Agent**: LangChain agent with three tools:
  1. `fetch_assignments` - Get assignments for a specific week
  2. `get_pending_assignments` - Get all pending assignments
  3. `create_calendar_event` - Create calendar events for study sessions
- **Keywords AI Integration**: Agent uses Keywords AI Gateway for LLM calls (with OpenAI fallback)
- **API Endpoints**:
  - `POST /api/ai/chat` - Main chat endpoint
  - `GET /api/ai/health` - Health check for AI services

### Agent Capabilities
- Understands natural language queries like "check for pending assignments this week and create a calendar entry"
- Automatically selects appropriate tools based on user request
- Can perform multi-step actions (fetch data → analyze → create events)
- Provides friendly, conversational responses

### Notes
- Agent uses GPT-4o-mini model through Keywords AI Gateway
- System prompt configured for study assistance role
- Error handling and fallback modes included
- Frontend already connected to `/api/ai/chat` endpoint

---

## [2026-01-31] - Implementation Complete

### Created
- `classly/backend/.env.example` - Environment variable template for configuration

### Summary
All core features have been implemented:
✅ AI tab added to sidebar navigation
✅ GPT-like chat interface created
✅ Keywords AI service integrated
✅ Supabase service for assignments
✅ Google Calendar service for events
✅ LangChain agent with tools
✅ API routes and endpoints
✅ Frontend-backend connection

### Next Steps
1. Install new dependencies: `cd classly/backend && source venv/bin/activate && pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure:
   - Get Keywords AI API key from https://app.keywordsai.co
   - Configure Supabase credentials (or use mock mode)
   - Configure Google Calendar OAuth (or use mock mode)
3. Restart backend server to load new routes
4. Test the AI agent with queries like:
   - "Check for pending assignments this week"
   - "Create calendar entries for my assignments"
   - "What assignments are due soon?"

### Notes
- All services have mock/fallback modes for development
- The agent will work with mock data even without full configuration
- Keywords AI integration provides observability and monitoring
- Frontend is fully functional and ready to use

---

## [2026-01-31] - Google Calendar OAuth Integration

### Created
- `classly/backend/routes/calendar_oauth.py` - OAuth routes for Google Calendar connection

### Modified
- `classly/backend/services/calendar_service.py` - Updated to support per-user OAuth credentials
- `classly/backend/services/ai_agent.py` - Updated to use user-specific calendar tools
- `classly/backend/routes/ai.py` - Updated to pass user_id to agent
- `classly/backend/app.py` - Registered calendar OAuth blueprint, added session secret key
- `classly/app/ai/page.tsx` - Added Google Calendar connection UI

### Features
- **OAuth Flow**: Complete Google Calendar OAuth 2.0 flow
  - `/api/calendar/oauth/authorize` - Redirects to Google consent screen
  - `/api/calendar/oauth/callback` - Handles OAuth callback and exchanges code for tokens
  - `/api/calendar/oauth/status` - Check if user's calendar is connected
  - `/api/calendar/oauth/disconnect` - Disconnect user's calendar
- **Token Storage**: Stores refresh tokens per user (in-memory for now, ready for database encryption)
- **Frontend UI**: 
  - "Connect Calendar" button when not connected
  - Connection status indicator when connected
  - Disconnect functionality
  - Automatic status checking on page load
- **User-Specific Agents**: AI agent now creates user-specific calendar tools

### OAuth Flow
1. User clicks "Connect Calendar" button
2. Redirected to Google OAuth consent screen
3. User authorizes access
4. Google redirects back with authorization code
5. Backend exchanges code for access + refresh tokens
6. Tokens stored per user
7. User redirected back to AI page with success message

### Security Notes
- Refresh tokens stored in-memory (production: encrypt and store in database)
- Session secret key required for OAuth flow
- State parameter used for CSRF protection
- CORS configured with credentials support

### Environment Variables Needed
- `GOOGLE_CALENDAR_CLIENT_ID` - From Google Cloud Console
- `GOOGLE_CALENDAR_CLIENT_SECRET` - From Google Cloud Console
- `GOOGLE_CALENDAR_REDIRECT_URI` - OAuth callback URL (default: http://localhost:5000/api/calendar/oauth/callback)
- `FLASK_SECRET_KEY` - Secret key for Flask sessions (auto-generated if not set)
- `FRONTEND_URL` - Frontend URL for redirects (default: http://localhost:3000)

### Next Steps
1. Set up Google Cloud Console OAuth credentials
2. Add authorized redirect URI: `http://localhost:5000/api/calendar/oauth/callback`
3. Test OAuth flow end-to-end
4. (Production) Move token storage to encrypted database)

---

## [2026-01-31] - Updated to Use Supabase User IDs and Store Tokens in Database

### Created
- `classly/backend/utils/auth_helpers.py` - Helper function to extract user ID from JWT tokens
- `classly/backend/migrations/create_calendar_tokens_table.sql` - SQL migration for calendar_tokens table

### Modified
- `classly/backend/services/calendar_service.py` - Updated to store/retrieve tokens from Supabase database
- `classly/backend/routes/calendar_oauth.py` - Updated to use real user IDs from JWT tokens
- `classly/backend/routes/ai.py` - Updated to use real user IDs from JWT tokens
- `classly/backend/requirements.txt` - Added PyJWT for JWT token decoding

### Key Changes
1. **User ID Extraction**: All routes now extract user ID from Supabase JWT token in Authorization header
2. **Database Storage**: Calendar tokens now stored in Supabase `calendar_tokens` table instead of in-memory
3. **Security**: 
   - Row Level Security (RLS) policies ensure users can only access their own tokens
   - Tokens linked to Supabase auth.users table via foreign key
4. **Fallback Support**: Still supports in-memory storage if Supabase not configured (for development)

### Database Schema
- Table: `calendar_tokens`
- Columns: user_id (UUID, FK to auth.users), refresh_token, access_token, token_uri, client_id, client_secret, scopes
- RLS Policies: Users can only CRUD their own tokens

### Important Notes
- **You still need YOUR OWN Google Calendar Client ID/Secret** - These identify YOUR app to Google
- Users authorize YOUR app to access THEIR calendars
- Each user's tokens are stored separately in the database
- Token refresh is handled automatically when tokens expire

### Setup Required
1. Run the SQL migration in Supabase SQL Editor to create the `calendar_tokens` table
2. Ensure Supabase Auth is configured and users can log in
3. Frontend should send JWT token in Authorization header: `Bearer <token>`

---

## 2025-01-31 - Free LLM Provider Support

### Changes
- **Updated `classly/backend/services/ai_agent.py`**:
  - Made LLM model configurable via `LLM_MODEL` environment variable
  - Default model changed to `gemini-1.5-flash` (free Google Gemini model)
  - Added model name to startup logs for debugging

### New Files
- **Created `classly/backend/FREE_LLM_SETUP.md`**:
  - Comprehensive guide for setting up free LLM providers
  - Instructions for Google Gemini, Groq, and Together AI
  - Troubleshooting tips and cost comparison

### Why This Change
- User doesn't have OpenAI credits
- Keywords AI Gateway supports 250+ LLM providers including free options
- Google Gemini offers a generous free tier perfect for development
- No code changes needed - just configuration!

### Next Steps for User
1. Get a free Google Gemini API key from https://aistudio.google.com/app/apikey
2. Add it to Keywords AI dashboard under LLM Provider Keys
3. Set `LLM_MODEL=gemini-1.5-flash` in `.env` file (or use default)
4. Restart backend server
5. Agent will now work without OpenAI credits!

### Supported Free Models
- `gemini-1.5-flash` - Fast, free tier (default) ✅ **Supports tool calling**
- `gemini-1.5-pro` - More capable, free tier ✅ **Supports tool calling**
- `groq/llama-3.1-8b-instant` - Very fast inference ⚠️ **Does NOT support tool calling**
- `groq/mixtral-8x7b-32768` - Larger context window ⚠️ **Does NOT support tool calling**
- `togethercomputer/llama-2-70b-chat` - Together AI free credits

---

## 2025-01-31 - Fixed Groq Tool Calling Issue

### Problem
- Groq models (llama-3.1-8b-instant, mixtral) don't support structured tool calling
- Error: `tool call validation failed: attempted to call tool which was not in request.tools`
- Agent couldn't use tools when using Groq models

### Solution
- **Updated `classly/backend/services/ai_agent.py`**:
  - Added automatic detection of Groq models
  - Auto-switches to `gemini-1.5-flash` when Groq is detected
  - Shows warning message to user about the limitation
  - Gemini supports tool calling properly

- **Updated `classly/backend/FREE_LLM_SETUP.md`**:
  - Added warning about Groq tool calling limitation
  - Recommended Google Gemini for agents with tools

- **Updated `.env` default**:
  - Changed default from `groq/llama-3.1-8b-instant` to `gemini-1.5-flash`
  - Gemini is better suited for agents with tool calling

### Why This Matters
- Tool calling is essential for the agent to:
  - Fetch assignments from database
  - Create calendar events
  - Get pending assignments
- Without tool calling, the agent can only chat, not perform actions
- Google Gemini has excellent tool calling support and is free

### Next Steps
1. Add Google Gemini API key to Keywords AI dashboard
2. Restart backend server
3. Agent will now work with tool calling!

---

## 2025-01-31 - Added Calendar Schedule Query Tool

### Changes
- **Updated `classly/backend/services/calendar_service.py`**:
  - Added `get_events()` method to fetch calendar events from Google Calendar
  - Added `_get_mock_events()` method for development/testing when calendar not connected
  - Supports time range queries (time_min, time_max) and max_results limit

- **Updated `classly/backend/services/ai_agent.py`**:
  - Created `create_calendar_schedule_tool_factory()` to create user-specific calendar query tool
  - Added `get_calendar_schedule` tool to the agent's tool list
  - Tool supports querying calendar for: "today", "tomorrow", "this week", "next week"
  - Updated system prompt to include calendar schedule checking capabilities

- **Updated `classly/backend/routes/ai.py`**:
  - Fixed missing `os` import that was causing NameError

### New Tool: `get_calendar_schedule`
The AI agent can now query the user's Google Calendar to:
- Check what events are scheduled for today, tomorrow, this week, or next week
- Find available time slots for scheduling study sessions
- Avoid double-booking when creating new calendar events
- Provide context-aware scheduling suggestions

### Example Queries
- "What's on my calendar today?"
- "Show me my schedule for this week"
- "What do I have scheduled tomorrow?"
- "Check my calendar and find a good time to study"

### How It Works
1. User asks about their calendar schedule
2. Agent calls `get_calendar_schedule` with appropriate period
3. Tool fetches events from Google Calendar (or returns mock data if not connected)
4. Agent uses this information to provide helpful scheduling advice

---

