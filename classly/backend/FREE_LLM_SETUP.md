# Free LLM Provider Setup Guide

Since you don't have OpenAI credits, you can use free/affordable LLM providers through Keywords AI Gateway. Here's how to set them up:

## Quick Start: Google Gemini (Recommended - Free Tier)

1. **Get Google Gemini API Key:**
   - Go to https://aistudio.google.com/app/apikey
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy your API key

2. **Add to Keywords AI Dashboard:**
   - Log into your Keywords AI dashboard
   - Go to **Settings → LLM Provider Keys** (or visit https://platform.keywordsai.co/platform/api/providers)
   - Click on the **Google** provider card
   - Add your Google Gemini API key
   - **IMPORTANT**: Make sure the provider is enabled/activated

3. **Configure Model in Keywords AI (if needed):**
   - Go to https://platform.keywordsai.co/platform/models
   - Check if `gemini-1.5-flash` is available in the model list
   - If not, you may need to add it or use an alternative model name
   - Try these model name formats if the default doesn't work:
     - `google/gemini-1.5-flash`
     - `gemini-pro`
     - `gemini-1.5-pro`

4. **Set Environment Variable:**
   ```bash
   # In your .env file
   LLM_MODEL=gemini-1.5-flash
   # Or try: LLM_MODEL=google/gemini-1.5-flash
   # Or try: LLM_MODEL=gemini-pro
   ```

4. **Restart your backend server**

## Alternative Free Options

### Option 2: Groq (Very Fast, Free Tier) ⚠️ LIMITATION

**⚠️ IMPORTANT: Groq models do NOT support tool calling/function calling!**
- If you use Groq, the agent will automatically switch to Google Gemini
- Groq is great for simple text generation but not for agents with tools
- **Recommendation: Use Google Gemini (Option 1) for agents with tools**

1. **Get Groq API Key:**
   - Go to https://console.groq.com/
   - Sign up for free account
   - Navigate to API Keys section
   - Create a new API key

2. **Add to Keywords AI Dashboard:**
   - Add your Groq API key to Keywords AI
   - Select "Groq" as the provider

3. **Set Environment Variable:**
   ```bash
   # Fast models available (but tool calling won't work):
   LLM_MODEL=groq/llama-3.1-8b-instant
   # or
   LLM_MODEL=groq/mixtral-8x7b-32768
   ```
   
**Note:** The agent will auto-detect Groq and switch to Gemini for tool calling support.

### Option 3: Together AI (Free Credits)

1. **Get Together AI API Key:**
   - Go to https://api.together.xyz/
   - Sign up (often provides free credits)
   - Get your API key

2. **Add to Keywords AI Dashboard:**
   - Add your Together AI API key
   - Select "Together AI" as the provider

3. **Set Environment Variable:**
   ```bash
   LLM_MODEL=togethercomputer/llama-2-70b-chat
   ```

## Supported Models

The agent works with any OpenAI-compatible model through Keywords AI Gateway. Popular free options:

- `gemini-1.5-flash` - Google Gemini (fast, free tier)
- `gemini-1.5-pro` - Google Gemini Pro (more capable, free tier)
- `groq/llama-3.1-8b-instant` - Groq (very fast)
- `groq/mixtral-8x7b-32768` - Groq (larger context)
- `togethercomputer/llama-2-70b-chat` - Together AI
- `anthropic/claude-3-haiku` - Anthropic (if you have credits)

## How It Works

1. **Keywords AI Gateway** acts as a unified interface to 250+ LLM providers
2. You add your provider API keys to Keywords AI dashboard
3. Your agent code uses the model name you specify
4. Keywords AI routes the request to the correct provider
5. All calls are logged and monitored in Keywords AI dashboard

## Testing Your Setup

After setting up a provider, test with:

```bash
cd classly/backend
source venv/bin/activate
python -c "
from services.ai_agent import get_agent
agent = get_agent('test_user')
result = agent.invoke({'input': 'What are my pending assignments?'})
print(result['output'])
"
```

## Troubleshooting

**Error: "Model not found" or "404 - Requested model is not available"**
- **Step 1**: Make sure you've added the provider API key to Keywords AI dashboard
  - Go to https://platform.keywordsai.co/platform/api/providers
  - Add your Google API key and select "Google" as provider
- **Step 2**: Check available models in Keywords AI
  - Go to https://platform.keywordsai.co/platform/models
  - See what Gemini models are available
  - Try using one of the available model names
- **Step 3**: Try different model name formats:
  ```bash
  # In your .env file, try these:
  LLM_MODEL=gemini-1.5-flash
  LLM_MODEL=google/gemini-1.5-flash
  LLM_MODEL=gemini-pro
  LLM_MODEL=gemini-1.5-pro
  ```
- **Step 4**: Verify the provider is enabled in Keywords AI dashboard
- **Step 5**: Restart your backend server after making changes

**Error: "Rate limit exceeded"**
- Free tiers have usage limits
- Try a different provider or wait for rate limit reset
- Consider upgrading to paid tier if needed

**Error: "Invalid API key"**
- Double-check your API key in Keywords AI dashboard
- Make sure you selected the correct provider type
- Regenerate API key if needed

## Cost Comparison

- **Google Gemini**: Free tier with generous limits
- **Groq**: Free tier, very fast inference
- **Together AI**: Free credits for new users
- **OpenAI**: Requires paid credits (what you're avoiding)

Your agent will work the same way regardless of which provider you choose!

