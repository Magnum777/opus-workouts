# ElevenLabs Voice Integration - Playbook

## Overview

**ElevenLabs** provides AI voice synthesis for natural, lifelike text-to-speech. Already have an API key configured. This skill enables OpenClaw to generate spoken audio from text.

## Use Cases for AI Co-Founder Stack

| Tier | Use Case |
|------|----------|
| **V1** | N/A - voice is V2 feature |
| **V2** | Voice output for AI responses, audio notifications, podcast generation |
| **V3** | Real-time conversational AI agents |

## API Overview

### Authentication
- **API Key**: Stored in `CREDENTIALS.md` as `ELEVENLABS_API_KEY`
- Environment variable: `ELEVENLABS_API_KEY`

### Available Models

| Model | Best For | Languages | Latency |
|-------|----------|-----------|---------|
| `eleven_v3` | Dramatic delivery, performances | 70+ | Higher |
| `eleven_multilingual_v2` | Stability, accent accuracy | 29 | Medium |
| `eleven_flash_v2_5` | Low latency, speed | 32 | **Lowest** |
| `eleven_turbo_v2_5` | Developer use cases | 32 | Low |

**Recommendation**: Use `eleven_flash_v2_5` for quick TTS, `eleven_multilingual_v2` for quality.

### Voice IDs
- Default voice: `JBFqnCBsd6RMkjVDRZzb` (Rachel - clear, neutral)
- Custom voices can be created via Voice Lab dashboard
- Voice cloning requires paid plan

## Integration Methods

### 1. Python SDK (Recommended)

```python
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import os

# Initialize with API key from environment
elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

# Generate speech
audio = elevenlabs.text_to_speech.convert(
    text="Hello! I'm your AI assistant.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_flash_v2_5",
    output_format="mp3_44100_128"
)

# Play locally
play(audio)

# Save to file
with open("output.mp3", "wb") as f:
    f.write(audio)
```

### 2. Streaming (Real-time)

```python
from elevenlabs import stream

audio_stream = elevenlabs.text_to_speech.stream(
    text="This text will stream as it's generated.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_flash_v2_5"
)

stream(audio_stream)  # Play as it streams
```

### 3. Command Line (curl)

```bash
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb" \
  -H "Accept: audio/mpeg" \
  -H "Content-Type: application/json" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -d '{
    "text": "Hello from the command line!",
    "model_id": "eleven_flash_v2_5"
  }' \
  -o output.mp3
```

## OpenClaw Skill Implementation

### Skill Structure

```
skills/elevenlabs/
├── SKILL.md
├── elevenlabs.py
└── requirements.txt
```

### SKILL.md Template

```yaml
---
name: elevenlabs
description: Generate natural AI voice audio from text using ElevenLabs TTS API.
metadata: { 
  "openclaw": { 
    "emoji": "🎙️", 
    "requires": { 
      "env": ["ELEVENLABS_API_KEY"],
      "bins": ["python"]
    } 
  } 
}
---

# ElevenLabs TTS

Generate speech audio from text using ElevenLabs voice synthesis.

## Commands

### speak <text>
Generate and play audio from text.

### speak-file <file>
Read text from file and generate audio.

### save <text> <filename>
Generate audio and save to file.

### voices
List available voices.

### stream <text>
Stream audio in real-time as it's generated.
```

### Python Wrapper Script

```python
#!/usr/bin/env python3
"""ElevenLabs TTS skill for OpenClaw"""

import sys
import os
import argparse
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

API_KEY = os.getenv("ELEVENLABS_API_KEY")
DEFAULT_VOICE = "JBFqnCBsd6RMkjVDRZzb"
DEFAULT_MODEL = "eleven_flash_v2_5"

def get_client():
    if not API_KEY:
        raise ValueError("ELEVENLABS_API_KEY not set")
    return ElevenLabs(api_key=API_KEY)

def speak(text, voice=DEFAULT_VOICE, model=DEFAULT_MODEL):
    client = get_client()
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice,
        model_id=model,
        output_format="mp3_44100_128"
    )
    play(audio)

def save(text, filename, voice=DEFAULT_VOICE, model=DEFAULT_MODEL):
    client = get_client()
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice,
        model_id=model
    )
    with open(filename, "wb") as f:
        f.write(audio)
    print(f"Saved to {filename}")

def list_voices():
    client = get_client()
    response = client.voices.search()
    for voice in response.voices:
        print(f"{voice.voice_id}: {voice.name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subcommands()
    
    sub.add_parser("speak", help="Speak text aloud")
    sub.add_parser("save", help="Save to file")
    sub.add_parser("voices", help="List voices")
    
    args = parser.parse_args()
```

## Pricing

| Free Tier | Paid Plans |
|-----------|-------------|
| 10,000 characters/month | $5-330/month |
| 3 custom voices | Unlimited voices |
| - | Higher quality voices |
| - | Priority support |

## Security Notes

- API key stored in environment variable, never in code
- Rate limits apply (based on plan)
- Audio output cannot contain harmful content (ElevenLabs content policy)

## Next Steps for V2

1. **Create skill folder** in `skills/elevenlabs/`
2. **Add API key** to `CREDENTIALS.md`
3. **Test with**: `python elevenlabs.py speak "Hello world!"`
4. **Integrate with OpenClaw** via TTS tool (already exists)
5. **Optional**: Create custom voice clone for Nova's persona

## References

- Docs: https://elevenlabs.io/docs/api-reference
- Python SDK: https://github.com/elevenlabs/elevenlabs-python
- Models: https://elevenlabs.io/docs/models
- Voice Lab: https://elevenlabs.io/voice-lab
