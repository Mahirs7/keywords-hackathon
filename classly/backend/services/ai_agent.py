"""
AI Agent Service
LangChain agent with tools for fetching assignments and creating calendar events
Uses Keywords AI Gateway for LLM calls
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.tools import tool

from services.keywords_ai import keywords_ai_service
from services.supabase_service import supabase_service
from services.calendar_service import calendar_service


@tool
def fetch_assignments(week: str = "this week") -> str:
    """
    Fetch assignments from the database. ONLY use this when the user specifically asks about assignments or homework.
    DO NOT use this for calendar-related queries. For calendar queries, use get_calendar_schedule instead.

    Args:
        week: Time period to fetch assignments for. Options: "this week", "next week", "all"

    Returns:
        JSON string with assignment details: title, due_at, url
    """
    try:
        now = datetime.now()

        if week == "this week":
            week_start = now - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=7)
        elif week == "next week":
            week_start = now - \
                timedelta(days=now.weekday()) + timedelta(days=7)
            week_end = week_start + timedelta(days=7)
        else:
            week_start = None
            week_end = None

        assignments = supabase_service.get_assignments(week_start, week_end)

        if not assignments:
            return "No assignments found for the specified period. The assignments table may not be set up yet."

        result = []
        for assignment in assignments:
            result.append({
                'title': assignment.get('title', 'Untitled Assignment'),
                'due_at': assignment.get('due_at', assignment.get('due_date', '')),
                'url': assignment.get('url', '')
            })

        import json
        return json.dumps(result, indent=2)
    except Exception as e:
        error_msg = str(e)
        if "Could not find the table" in error_msg or "PGRST205" in error_msg:
            return "The assignments table is not set up in the database yet. Please set up the assignments table in Supabase first."
        return f"Error fetching assignments: {error_msg}"


def create_calendar_event_tool_factory(user_id: str):
    """Factory function to create a calendar event tool with user_id"""
    @tool
    def create_calendar_event(
        title: str,
        start_time: str,
        duration_hours: float = 2.0,
        description: str = ""
    ) -> str:
        """
        Create a calendar event for study time in the user's Google Calendar.

        Args:
            title: Event title (e.g., "Study: Problem Set 4")
            start_time: Start time in ISO format (YYYY-MM-DDTHH:MM:SS) or relative (e.g., "tomorrow 2pm")
            duration_hours: Duration of the event in hours (default: 2.0)
            description: Optional description for the event

        Returns:
            String confirmation with event details
        """
        try:
            from datetime import timezone
            import pytz

            # Default to America/Chicago timezone (can be made configurable)
            # When user says "2pm", they mean 2pm in their local timezone
            user_tz = pytz.timezone('America/Chicago')  # Default timezone

            # Parse start_time
            if "tomorrow" in start_time.lower():
                # Get tomorrow in user's local timezone
                tomorrow_local = datetime.now(user_tz) + timedelta(days=1)

                if "pm" in start_time.lower() or "am" in start_time.lower():
                    # Extract hour from time string
                    hour = 14  # Default 2pm
                    minute = 0

                    # Try to parse hour
                    import re
                    time_match = re.search(
                        r'(\d{1,2})\s*(am|pm)', start_time.lower())
                    if time_match:
                        hour_val = int(time_match.group(1))
                        am_pm = time_match.group(2)
                        if am_pm == 'pm' and hour_val != 12:
                            hour = hour_val + 12
                        elif am_pm == 'am' and hour_val == 12:
                            hour = 0
                        else:
                            hour = hour_val

                    start = tomorrow_local.replace(
                        hour=hour, minute=minute, second=0, microsecond=0)
                else:
                    # Default to 2pm local time
                    start = tomorrow_local.replace(
                        hour=14, minute=0, second=0, microsecond=0)
            else:
                try:
                    # Try parsing ISO format
                    start = datetime.fromisoformat(
                        start_time.replace('Z', '+00:00'))
                    # If no timezone, assume it's in user's local timezone
                    if start.tzinfo is None:
                        start = user_tz.localize(start)
                    else:
                        # Convert to user's timezone first, then we'll convert to UTC later
                        start = start.astimezone(user_tz)
                except:
                    # Default to tomorrow 2pm in user's local timezone
                    tomorrow_local = datetime.now(user_tz) + timedelta(days=1)
                    start = tomorrow_local.replace(
                        hour=14, minute=0, second=0, microsecond=0)

            # Convert to UTC for API call (but keep original for display)
            start_utc = start.astimezone(timezone.utc)
            end_utc = start_utc + timedelta(hours=duration_hours)

            event = calendar_service.create_event(
                user_id=user_id,
                title=title,
                start_time=start_utc,
                end_time=end_utc,
                description=description,
                # Pass user's timezone so Google Calendar displays it correctly
                timezone=str(user_tz)
            )

            if event.get('status') == 'created' or event.get('status') == 'mock_created':
                note = event.get('note', '')
                return f"✅ Calendar event created: '{title}' on {start.strftime('%Y-%m-%d at %I:%M %p')} for {duration_hours} hours. {note}"
            else:
                return f"❌ Failed to create calendar event: {event.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error creating calendar event: {str(e)}"

    return create_calendar_event


@tool
def get_pending_assignments() -> str:
    """
    Get all pending (not submitted) assignments. ONLY use this when the user specifically asks about pending assignments or homework.
    DO NOT use this for calendar-related queries. For calendar queries, use get_calendar_schedule instead.

    Returns:
        JSON string with assignment details: title, due_at, url
    """
    try:
        assignments = supabase_service.get_pending_assignments()

        if not assignments:
            return "No pending assignments found. The assignments table may not be set up yet."

        result = []
        for assignment in assignments:
            result.append({
                'title': assignment.get('title', 'Untitled Assignment'),
                'due_at': assignment.get('due_at', assignment.get('due_date', '')),
                'url': assignment.get('url', '')
            })

        import json
        return json.dumps(result, indent=2)
    except Exception as e:
        error_msg = str(e)
        if "Could not find the table" in error_msg or "PGRST205" in error_msg:
            return "The assignments table is not set up in the database yet. Please set up the assignments table in Supabase first."
        return f"Error fetching pending assignments: {error_msg}"


def create_calendar_schedule_tool_factory(user_id: str):
    """Factory function to create a calendar schedule query tool with user_id"""
    @tool
    def get_calendar_schedule(
        period: str = "this week",
        max_results: int = 10
    ) -> str:
        """
        Get calendar events/schedule from the user's Google Calendar. USE THIS TOOL for any calendar-related queries.
        This is the PRIMARY tool for viewing calendar events, schedule, or checking what's on the calendar.
        Use this when the user asks about their calendar, schedule, events, or what they have planned.

        Args:
            period: Time period to fetch events for. Options: "today", "this week", "next week", "tomorrow"
            max_results: Maximum number of events to return (default: 10)

        Returns:
            Human-readable string with calendar event details including title, start time, end time, description, and location.
            If calendar is not connected, returns a message indicating the need to connect Google Calendar.
        """
        try:
            # Check if user has connected their calendar
            if not calendar_service.is_user_connected(user_id):
                return f"⚠️ Google Calendar is not connected. Please connect your Google Calendar first to view your schedule for {period}."

            from datetime import timezone
            now = datetime.now(timezone.utc)

            # Parse period into time range (all times in UTC)
            if period == "today":
                # Get today in UTC, but we need to consider user's local timezone
                # For now, use UTC day boundaries
                time_min = now.replace(
                    hour=0, minute=0, second=0, microsecond=0)
                time_max = now.replace(
                    hour=23, minute=59, second=59, microsecond=999999)
            elif period == "tomorrow":
                tomorrow = now + timedelta(days=1)
                time_min = tomorrow.replace(
                    hour=0, minute=0, second=0, microsecond=0)
                time_max = tomorrow.replace(
                    hour=23, minute=59, second=59, microsecond=999999)
            elif period == "this week":
                week_start = now - timedelta(days=now.weekday())
                time_min = week_start.replace(
                    hour=0, minute=0, second=0, microsecond=0)
                time_max = week_start + timedelta(days=7)
            elif period == "next week":
                week_start = now - \
                    timedelta(days=now.weekday()) + timedelta(days=7)
                time_min = week_start.replace(
                    hour=0, minute=0, second=0, microsecond=0)
                time_max = week_start + timedelta(days=7)
            else:
                # Default to next 7 days
                time_min = now
                time_max = now + timedelta(days=7)

            try:
                events = calendar_service.get_events(
                    user_id=user_id,
                    time_min=time_min,
                    time_max=time_max,
                    max_results=max_results
                )
            except Exception as e:
                # Calendar is connected but API call failed
                error_msg = str(e)
                return f"⚠️ Error fetching calendar events: {error_msg}"

            if not events:
                return f"No calendar events found for {period}."

            # Format events in a human-readable way
            result_lines = [f"📅 Calendar Events for {period}:\n"]

            for i, event in enumerate(events, 1):
                title = event.get('title', 'Untitled Event')
                start_str = event.get('start', '')
                end_str = event.get('end', '')
                description = event.get('description', '')
                location = event.get('location', '')
                status = event.get('status', 'confirmed')

                # Parse and format dates
                try:
                    if 'T' in start_str:
                        start_dt = datetime.fromisoformat(
                            start_str.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(
                            end_str.replace('Z', '+00:00'))

                        # Format date and time
                        date_str = start_dt.strftime('%A, %B %d, %Y')
                        start_time = start_dt.strftime('%I:%M %p')
                        end_time = end_dt.strftime('%I:%M %p')

                        time_str = f"{start_time} - {end_time}"
                    else:
                        # All-day event
                        start_dt = datetime.fromisoformat(start_str)
                        date_str = start_dt.strftime('%A, %B %d, %Y')
                        time_str = "All day"
                except:
                    date_str = start_str
                    time_str = end_str

                result_lines.append(f"\n{i}. {title}")
                result_lines.append(f"   📅 {date_str}")
                result_lines.append(f"   ⏰ {time_str}")

                if location:
                    result_lines.append(f"   📍 {location}")
                if description:
                    # Truncate long descriptions
                    desc = description[:100] + \
                        "..." if len(description) > 100 else description
                    result_lines.append(f"   📝 {desc}")

                # Check if this is mock data
                if event.get('id', '').startswith('mock_'):
                    result_lines.append(
                        f"   ⚠️ (Mock data - connect calendar for real events)")

            return "\n".join(result_lines)

        except Exception as e:
            error_msg = str(e)
            if "accessNotConfigured" in error_msg or "API has not been used" in error_msg:
                return f"⚠️ Google Calendar API is not enabled. Please enable it in Google Cloud Console, then reconnect your calendar."
            return f"Error fetching calendar schedule: {error_msg}"

    return get_calendar_schedule


def create_agent(user_id: str = "user_123"):
    """Create and configure the AI agent with tools for a specific user"""

    import os
    # Get model from environment variable, default to OpenAI
    # OpenAI models support tool calling properly
    # Options: gpt-4o-mini (default, cost-effective), gpt-4o, gpt-4-turbo, gpt-3.5-turbo
    model = os.getenv('LLM_MODEL', 'gpt-4o-mini')

    # Get LLM client from Keywords AI service
    try:
        if keywords_ai_service.is_configured():
            # Use Keywords AI Gateway with LangChain
            # Keywords AI uses: https://api.keywordsai.co/api/chat/completions
            # LangChain's ChatOpenAI expects base_url, it will add /chat/completions
            # So we need: https://api.keywordsai.co/api
            gateway_url = keywords_ai_service.gateway_url
            llm = ChatOpenAI(
                model=model,
                temperature=0.7,
                api_key=keywords_ai_service.api_key,
                base_url=gateway_url
            )
            print(f"✅ Using Keywords AI Gateway: {gateway_url}")
            print(f"   Model: {model}")
            print(f"   All LLM calls and tool invocations will be logged in Keywords AI")
        else:
            raise ValueError("Keywords AI not configured")
    except Exception as e:
        print(f"Warning: Could not initialize Keywords AI client: {e}")
        print("Falling back to direct OpenAI (if OPENAI_API_KEY is set)")
        # Fallback to direct OpenAI if Keywords AI not configured
        llm = ChatOpenAI(
            model=model,
            temperature=0.7
        )

    # Create user-specific calendar tools
    create_calendar_event = create_calendar_event_tool_factory(user_id)
    get_calendar_schedule = create_calendar_schedule_tool_factory(user_id)

    # Define tools - put calendar tools first to prioritize them
    tools = [get_calendar_schedule, create_calendar_event,
             fetch_assignments, get_pending_assignments]

    # System prompt for the agent
    system_prompt = """You are a helpful AI study assistant. Your role is to help students manage their coursework and schedule study time.

You have access to the following tools:
1. get_calendar_schedule - Get calendar events/schedule from the user's Google Calendar (USE THIS for viewing calendar/schedule)
2. create_calendar_event - Create calendar events for study sessions
3. fetch_assignments - Get assignments for a specific week (may not be available if database table doesn't exist)
4. get_pending_assignments - Get all pending assignments (may not be available if database table doesn't exist)

IMPORTANT: When a user asks about their calendar, schedule, or events, you MUST use get_calendar_schedule first.
- "What's on my calendar?" → Use get_calendar_schedule
- "Show me my schedule" → Use get_calendar_schedule
- "What events do I have?" → Use get_calendar_schedule
- "Check my calendar" → Use get_calendar_schedule
- "View my calendar" → Use get_calendar_schedule

When a user asks you to:
- Check calendar/schedule/view events: ALWAYS use get_calendar_schedule FIRST
- Check for assignments: Use fetch_assignments or get_pending_assignments (only if user specifically asks about assignments)
- Create calendar entries: Use create_calendar_event with appropriate times
- Plan study schedule: First use get_calendar_schedule to see what's scheduled, then fetch assignments if needed, then create calendar events
- Find free time: Use get_calendar_schedule to see existing events, then suggest available slots

Always be helpful, clear, and provide specific details about what actions you're taking.
When creating calendar events, suggest reasonable time slots (e.g., 2-3 hours for assignments).
If you don't have enough information, ask the user for clarification.

Format your responses in a friendly, conversational manner."""

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create agent
    agent = create_openai_tools_agent(llm, tools, prompt)

    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )

    return agent_executor


# Agent instances per user
_agent_instances = {}


def get_agent(user_id: str = "user_123"):
    """Get or create the agent instance for a specific user"""
    if user_id not in _agent_instances:
        _agent_instances[user_id] = create_agent(user_id)
    return _agent_instances[user_id]
