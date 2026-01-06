# Telugu News Media Processing Suite

A comprehensive AI-powered media processing toolkit for Telugu news content generation, including video summarization, audio transcription, image analysis, and text-to-speech conversion.

## Quick Install

### Prerequisites

- Python 3.9+
- FFmpeg (required for video/audio processing)

### 1. Install FFmpeg

**Windows (using Chocolatey):**
```bash
choco install ffmpeg
```

**Windows (Manual):**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System PATH

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg -y
```

### 2. Clone & Install

```bash
# Clone repository
git clone <your-repo-url>
cd telugu-news-suite

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-openai-key
SARVAM_API_KEY=your-sarvam-key
ELEVENLABS_API_KEY=your-elevenlabs-key
GUPSHUP_API_KEY=your-gupshup-key
GUPSHUP_SOURCE_NUMBER=91XXXXXXXXXX
GUPSHUP_APP_NAME=your-app-name
```

## Requirements File

Create `requirements.txt`:

```
# Core
python-dotenv>=1.0.0
flask>=3.0.0
requests>=2.31.0

# AI/ML
openai>=1.12.0
sarvamai>=0.1.0
elevenlabs>=0.2.0

# Media Processing
opencv-python>=4.8.0
moviepy>=1.0.3
pydub>=0.25.1
numpy>=1.24.0

# Web Interface
streamlit>=1.30.0

# Utilities
Pillow>=10.0.0
```

## Run Applications

### Main Streamlit App (Recommended)
```bash
streamlit run app.py
```

### WhatsApp Bot Server
```bash
python webhook_server.py
```

### TTS Generator
```bash
streamlit run tts_app.py
```

### Video Summarizer
```bash
streamlit run video_summarizer.py
```

### Content Moderation Pipeline
```bash
python moderation_pipeline.py
```

## Project Structure

```
telugu-news-suite/
├── app.py                 # Main Streamlit interface
├── shared.py              # Shared utilities & config
├── video.py               # Video processing
├── audio.py               # Audio processing
├── image.py               # Image processing
├── main1.py               # Core AI functions
├── webhook_server.py      # WhatsApp webhook
├── video_summarizer.py    # Video summarization
├── tts_app.py             # Text-to-speech
├── moderation_pipeline.py # Content moderation
├── incident_processor.py  # Duplicate detection
├── requirements.txt
├── .env
└── output/                # Generated files
    ├── video/
    ├── audio/
    ├── image/
    └── text/
```

## Features

| Feature | Description |
|---------|-------------|
| 📺 Script Generation | AI-powered Telugu news scripts |
| 🎙️ Text-to-Speech | 9 anchor voices via Sarvam AI |
| 🎬 Video Summarizer | Smart 15/30/60s summaries |
| 📱 WhatsApp Bot | Media processing via WhatsApp |
| 🔍 Content Moderation | AI/deepfake detection |
| 📊 Auto News Detection | Breaking news prioritization |

## Troubleshooting

**FFmpeg not found:**
```bash
# Verify installation
ffmpeg -version
```

**Module not found:**
```bash
pip install <missing-module> --break-system-packages
```

**API errors:**
- Verify API keys in `.env`
- Check API quotas/limits

## License

MIT License
