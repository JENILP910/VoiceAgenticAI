# Marathi Voice Agent with Open-Source LLMs

## Overview
This updated version supports multiple open-source LLM providers:
- **Groq** (Recommended) - Fast inference with Llama 3.3, Mixtral, Gemma
- **Ollama** - Run models locally on your machine
- **OpenRouter** - Access to various open-source models

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install PyAudio (for microphone)

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**Mac:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt-get install python3-pyaudio
```

### 3. Choose Your LLM Provider

#### Option A: Groq (Recommended - Fast & Free)

1. Get API key from https://console.groq.com
2. Set environment variables:

```bash
export LLM_PROVIDER=groq
export LLM_API_KEY=your-groq-api-key
export LLM_MODEL=llama-3.3-70b-versatile
```

**Available Groq Models:**
- `llama-3.3-70b-versatile` (Recommended - Best quality)
- `llama-3.1-70b-versatile` (Fast, good quality)
- `mixtral-8x7b-32768` (Good for long context)
- `gemma2-9b-it` (Lightweight, fast)

#### Option B: Ollama (Local - No API Key Needed)

1. Install Ollama from https://ollama.ai
2. Pull a model:

```bash
ollama pull llama3.2
```

3. Start Ollama server:

```bash
ollama serve
```

4. Set environment variables:

```bash
export LLM_PROVIDER=ollama
export LLM_MODEL=llama3.2
```

**Available Ollama Models:**
- `llama3.2` (3B/1B - Fast)
- `llama3.1` (8B/70B - Better quality)
- `mistral` (7B - Good balance)
- `gemma2` (2B/9B - Fast)

#### Option C: OpenRouter (Most Options)

1. Get API key from https://openrouter.ai
2. Set environment variables:

```bash
export LLM_PROVIDER=openrouter
export LLM_API_KEY=your-openrouter-api-key
export LLM_MODEL=meta-llama/llama-3.1-70b-instruct
```

**Popular OpenRouter Models:**
- `meta-llama/llama-3.1-70b-instruct`
- `mistralai/mixtral-8x7b-instruct`
- `google/gemma-2-9b-it`

### 4. Run the Agent

```bash
python Voice_agent.py
```

## Configuration Examples

### Groq (Fast, Free Tier Available)
```bash
export LLM_PROVIDER=groq
export LLM_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
export LLM_MODEL=llama-3.3-70b-versatile
python Voice_agent.py
```

### Ollama (Fully Local, Private)
```bash
# Make sure Ollama is running
ollama serve &

export LLM_PROVIDER=ollama
export LLM_MODEL=llama3.2
python Voice_agent.py
```

### OpenRouter (Pay-per-use)
```bash
export LLM_PROVIDER=openrouter
export LLM_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxx
export LLM_MODEL=meta-llama/llama-3.1-70b-instruct
python Voice_agent.py
```

## Key Features

✅ **Multi-Provider Support** - Switch between Groq, Ollama, OpenRouter
✅ **Voice Input/Output** - Marathi speech recognition and TTS
✅ **Agentic Architecture** - Planner → Executor → Evaluator loop
✅ **Multiple Tools** - Info extraction, eligibility check, scheme details
✅ **Memory & Contradiction Detection** - Tracks conversation history
✅ **Failure Handling** - Graceful error recovery

## Testing the Agent

1. Start the agent
2. Speak in Marathi when prompted
3. Example queries:
   - "माझे वय ३० वर्षे आहे आणि मी शेतकरी आहे"
   - "मला कोणत्या योजना मिळू शकतात?"
   - "प्रधानमंत्री आवास योजनेबद्दल सांगा"

## Troubleshooting

### Microphone Issues
```bash
# Test microphone
python -c "import speech_recognition as sr; r = sr.Recognizer(); print('Mic OK')"
```

### Groq Rate Limits
- Free tier: 30 requests/minute
- If limited, wait or upgrade plan

### Ollama Not Running
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags
```

### JSON Parsing Errors
- The code includes robust JSON cleaning
- If issues persist, try a different model

## Model Recommendations

**For Best Quality:**
- Groq: `llama-3.3-70b-versatile`
- OpenRouter: `meta-llama/llama-3.1-70b-instruct`

**For Speed:**
- Groq: `gemma2-9b-it`
- Ollama: `llama3.2`

**For Local/Private:**
- Ollama: `llama3.1` or `mistral`

## Cost Comparison

| Provider | Model | Cost | Speed | Quality |
|----------|-------|------|-------|---------|
| Groq | llama-3.3-70b | Free* | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ |
| Ollama | llama3.2 | Free | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ |
| OpenRouter | llama-3.1-70b | $0.40/1M | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ |

*Groq free tier: 30 req/min, 14,400 req/day

## Contributing

Feel free to add support for more LLM providers:
- Together AI
- Replicate
- HuggingFace Inference API
- Anyscale Endpoints

## License

MIT License - Feel free to use and modify!