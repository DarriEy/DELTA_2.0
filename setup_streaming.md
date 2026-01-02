# DELTA Streaming Setup Guide

## 1. Get Your API Keys

### Hugging Face (Free)
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with "Read" permissions
3. Copy the token

### ElevenLabs (Free Tier: 10k characters/month)
1. Go to https://elevenlabs.io/
2. Sign up for free account
3. Go to Profile → API Keys
4. Copy your API key

## 2. Update Environment Variables

Replace the placeholder values in your `.env` file:

```bash
# Replace with your actual keys
HUGGINGFACE_API_KEY=hf_your_actual_token_here
ELEVENLABS_API_KEY=your_actual_elevenlabs_key_here

# These are already set for streaming
LLM_PROVIDER=huggingface
TTS_PROVIDER=elevenlabs
```

## 3. Install Dependencies

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Test the Setup

Start your backend:
```bash
uvicorn api.main:app --reload
```

Test streaming endpoints:
- LLM streaming: `POST /chat/process_stream`
- TTS streaming: `POST /chat/tts_stream`

## 5. Available Models

### Hugging Face (Free)
- `microsoft/DialoGPT-medium` (default)
- `microsoft/DialoGPT-large`
- `facebook/blenderbot-400M-distill`

### ElevenLabs Voices (Free)
- `21m00Tcm4TlvDq8ikWAM` - Rachel (default)
- `AZnzlk1XvdvUeBnXmlld` - Domi
- `EXAVITQu4vr4xnSDxMaL` - Bella

## 6. Usage in Frontend

The existing streaming endpoints will now use the new providers automatically based on your `.env` settings.
