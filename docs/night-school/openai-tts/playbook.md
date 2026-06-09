# OpenAI TTS Integration

**Setup Date:** 2026-04-26
**Service:** OpenAI Text-to-Speech
**Models:** tts-1, tts-1-hd

## Voices Available

| Voice | Style | Best For |
|-------|-------|----------|
| **alloy** | Neutral, balanced | General purpose |
| **echo** | Warm, friendly | Conversational |
| **fable** | British, professional | Narration |
| **onyx** | Deep, authoritative | Serious content |
| **nova** | Bright, energetic | Friendly/helpful |
| **shimmer** | Soft, warm | Storytelling |

**Recommendation:** `nova` for Nova AI (matches name), `echo` for warm assistant feel

## API Endpoint

```bash
curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Hello, I am Nova!",
    "voice": "nova",
    "response_format": "mp3"
  }' \
  --output speech.mp3
```

## Python Integration

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_voice(text, voice="nova", output_file="output.mp3"):
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
        response_format="mp3"
    )
    response.stream_to_file(output_file)
    return output_file

# Example usage
# generate_voice("Hello Opus, I'm ready to help!", voice="echo")
```

## Pricing

- **tts-1:** $0.015 / 1K characters
- **tts-1-hd:** $0.030 / 1K characters (higher quality)

## Discord Integration

1. Generate voice file
2. Post to channel with `MEDIA:path` directive
3. Or use `[[audio_as_voice]]` for voice-note style

## Test Commands

```python
# Quick test
from openai import OpenAI
client = OpenAI()

speech = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input="This is Nova, testing OpenAI text to speech!"
)
speech.stream_to_file("test.mp3")
```

## Config

Add to `.env`:
```
OPENAI_API_KEY=your_key_here
```

Already configured in OpenClaw via model providers.
