import os
import json
import base64
import mimetypes
import subprocess
import re
import csv
import wave
import struct
from datetime import datetime
from typing import Literal, Any, Dict, Optional, List
import tempfile

from openai import OpenAI
from pydub import AudioSegment
from sarvamai import SarvamAI


# =========================
# CONFIGURATION
# =========================
def get_output_base_path():
    """Get the base output path - Windows Desktop path"""
    try:
        desktop = r"C:\Users\GLOBAL T\Desktop\output"
        os.makedirs(desktop, exist_ok=True)
        return desktop
    except Exception as e:
        print(f"⚠️ Could not access Desktop, using local 'output' folder: {e}")
        fallback = os.path.join(os.getcwd(), "output")
        os.makedirs(fallback, exist_ok=True)
        return fallback


OUTPUT_BASE_PATH = get_output_base_path()

TELUGU_DIGITS = {
    '0': '౦', '1': '౧', '2': '౨', '3': '౩', '4': '౪',
    '5': '౫', '6': '౬', '7': '౭', '8': '౮', '9': '౯'
}

TV_COMMAND_TYPES = {
    "BREAKING NEWS": {
        "icon": "🚨", "color": "#ff4444",
        "description": "Urgent breaking news report",
        "tv_style": "BREAKING NEWS BANNER",
        "sample_opening": "ఈ గంటలో మీకు బ్రేకింగ్ న్యూస్...",
        "voice_tone": "Urgent, dramatic",
        "instructions": [
            "Open with dramatic urgency",
            "Use present tense and active voice",
            "Keep sentences short and punchy",
            "Emphasize the breaking nature",
            "Build tension and importance",
            "End with forward-looking statement"
        ]
    },
    "LIVE REPORT": {
        "icon": "📡", "color": "#ffaa00",
        "description": "Live from location reporting",
        "tv_style": "LIVE TAG + LOCATION",
        "sample_opening": "శుభసాయంత్రం, నేను ప్రత్యక్ష ప్రసారంలో...",
        "voice_tone": "Present tense, energetic",
        "instructions": [
            "Start with location introduction",
            "Use present continuous tense",
            "Describe the scene vividly",
            "Include sensory details",
            "End with signoff from location"
        ]
    },
    "PRIME TIME": {
        "icon": "🌟", "color": "#ffcc00",
        "description": "Prime time detailed analysis",
        "tv_style": "PRIME TIME SPECIAL REPORT",
        "sample_opening": "శుభసాయంత్రం, ఈ రాత్రి ప్రత్యేక కథనానికి స్వాగతం...",
        "voice_tone": "Authoritative, analytical, in-depth",
        "instructions": [
            "Formal greeting and introduction",
            "Provide comprehensive background",
            "Include expert perspectives",
            "Connect to bigger picture",
            "Professional closing remarks"
        ]
    },
    "HEADLINE NEWS": {
        "icon": "📰", "color": "#44aaff",
        "description": "Top stories bulletin",
        "tv_style": "HEADLINE NEWS BULLETIN",
        "sample_opening": "ఈ రాత్రి టాప్ స్టోరీలు ఇవి...",
        "voice_tone": "Clear, professional",
        "instructions": [
            "Standard news opening",
            "Present facts clearly and directly",
            "Cover who, what, when, where, why",
            "Maintain objective tone",
            "Standard professional closing"
        ]
    },
    "SPORTS NEWS": {
        "icon": "⚽", "color": "#00aa44",
        "description": "Sports highlights and scores",
        "tv_style": "SPORTS CENTER",
        "sample_opening": "ఈ రాత్రి స్పోర్ట్స్‌లో...",
        "voice_tone": "Energetic, exciting",
        "instructions": [
            "Start with excitement and energy",
            "Lead with the main result",
            "Describe key moments dramatically",
            "Highlight player performances",
            "Preview upcoming action"
        ]
    },
    "WEATHER REPORT": {
        "icon": "🌧️", "color": "#8844ff",
        "description": "Weather forecast and alerts",
        "tv_style": "WEATHER ALERT",
        "sample_opening": "వాతావరణ పరిస్థితులను చూద్దాం...",
        "voice_tone": "Clear, informative, sometimes urgent",
        "instructions": [
            "Current conditions first",
            "Use clear, simple language",
            "Include specific temperatures",
            "Warn of any hazards",
            "End with extended outlook"
        ]
    },
    "BUSINESS NEWS": {
        "icon": "📈", "color": "#00cccc",
        "description": "Financial markets and economy",
        "tv_style": "MARKET UPDATE",
        "sample_opening": "ఈ రోజు మార్కెట్ల వైపు చూస్తే...",
        "voice_tone": "Professional, factual, numbers-focused",
        "instructions": [
            "Lead with major market movements",
            "Cite specific numbers and percentages",
            "Explain market reactions",
            "Include expert analysis",
            "Forward-looking statements"
        ]
    },
    "ENTERTAINMENT NEWS": {
        "icon": "🎬", "color": "#ff66aa",
        "description": "Celebrity, movies, TV shows",
        "tv_style": "ENTERTAINMENT TONIGHT",
        "sample_opening": "ఈ రాత్రి వినోద వార్తల్లో...",
        "voice_tone": "Light, engaging, conversational",
        "instructions": [
            "Conversational but professional tone",
            "Lead with biggest celebrity story",
            "Keep it fun and engaging",
            "Include interesting details",
            "Tease upcoming entertainment"
        ]
    },
    "HEALTH NEWS": {
        "icon": "🏥", "color": "#ff6666",
        "description": "Medical updates and health alerts",
        "tv_style": "HEALTH WATCH",
        "sample_opening": "ఈ రాత్రి ఆరోగ్య వార్తల్లో...",
        "voice_tone": "Caring, informative, reassuring",
        "instructions": [
            "Caring and concerned tone",
            "Present medical information clearly",
            "Include expert advice",
            "Offer practical guidance",
            "Encourage healthy actions"
        ]
    },
    "CRIME REPORT": {
        "icon": "🚔", "color": "#333333",
        "description": "Police, crime, investigations",
        "tv_style": "CRIME WATCH",
        "sample_opening": "పోలీసులు దర్యాప్తు చేస్తున్నారు...",
        "voice_tone": "Serious, factual",
        "instructions": [
            "Serious, respectful tone",
            "Stick to confirmed facts",
            "Avoid graphic details",
            "Include official statements",
            "End with investigation status"
        ]
    },
    "POLITICAL NEWS": {
        "icon": "🏛️", "color": "#6666ff",
        "description": "Government, elections, policy",
        "tv_style": "POLITICAL BRIEFING",
        "sample_opening": "ఈ రోజు రాజకీయ పరిణామాల్లో...",
        "voice_tone": "Neutral, balanced, authoritative",
        "instructions": [
            "Maintain strict neutrality",
            "Present all perspectives",
            "Quote officials directly",
            "Explain policy implications",
            "Note what's ahead"
        ]
    },
    "TECH NEWS": {
        "icon": "💻", "color": "#00aaff",
        "description": "Technology, gadgets, internet",
        "tv_style": "TECH UPDATE",
        "sample_opening": "టెక్నాలజీ వార్తల్లో...",
        "voice_tone": "Futuristic, innovative, explanatory",
        "instructions": [
            "Make tech accessible",
            "Explain complex concepts simply",
            "Show enthusiasm for innovation",
            "Connect to daily life",
            "Preview upcoming tech"
        ]
    }
}

VOICE_PRESETS = {
    "anushka": {"name": "Anushka", "gender": "Female", "style": "Clear & Professional"},
    "vidya": {"name": "Vidya", "gender": "Female", "style": "General Purpose"},
    "manisha": {"name": "Manisha", "gender": "Female", "style": "Educational"},
    "arya": {"name": "Arya", "gender": "Female", "style": "News & Announcements"},
    "meera": {"name": "Meera", "gender": "Female", "style": "Conversational"},
    "kavya": {"name": "Kavya", "gender": "Female", "style": "Storytelling"},
    "abhilash": {"name": "Abhilash", "gender": "Male", "style": "Authoritative"},
    "karun": {"name": "Karun", "gender": "Male", "style": "Conversational"},
    "hitesh": {"name": "Hitesh", "gender": "Male", "style": "General Purpose"}
}


# =========================
# CSV LOGGING SYSTEM
# =========================
def get_current_timestamp():
    """Get current timestamp string"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_output_base_exists():
    """Ensure base output directory exists"""
    base_path = get_output_base_path()
    os.makedirs(base_path, exist_ok=True)
    return base_path


def ensure_csv_exists():
    """Ensure the CSV file exists with headers in the base output directory"""
    base_path = ensure_output_base_exists()
    csv_path = os.path.join(base_path, "processing_log.csv")

    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Date', 'Time', 'Timestamp', 'Source Type', 'Input File Name',
                'Input File Size (MB)', 'Language', 'News Format', 'Location',
                'Incident Time', 'AI Model Used', 'Output File Name', 'Output File Path',
                'Audio Generated', 'Status', 'Notes'
            ])


def log_to_csv(
    source_type: str,
    input_file_name: Optional[str],
    input_file_size_mb: float,
    languages: List[str],
    news_format: str,
    location: Optional[str],
    incident_time: Optional[str],
    ai_model: str,
    output_files: List[str],
    audio_generated: bool = False,
    status: str = "SUCCESS",
    notes: str = "",
    output_folder: str = ""
):
    """Log processing details to CSV file"""
    try:
        ensure_csv_exists()
        
        base_path = get_output_base_path()
        csv_path = os.path.join(base_path, "processing_log.csv")
        
        now = datetime.now()
        date_str = now.strftime("%d-%m-%Y")
        time_str = now.strftime("%H:%M:%S")
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        
        output_file_names = [os.path.basename(f) for f in output_files] if output_files else []
        
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                date_str,
                time_str,
                timestamp_str,
                source_type,
                input_file_name or "N/A",
                f"{input_file_size_mb:.2f}",
                " | ".join(languages) if languages else "te",
                news_format,
                location or "N/A",
                incident_time or "N/A",
                ai_model,
                " | ".join(output_file_names) if output_file_names else "N/A",
                output_folder or base_path,
                "Yes" if audio_generated else "No",
                status,
                notes
            ])
    except Exception as e:
        print(f"Warning: Could not log to CSV: {e}")


# =========================
# TTS FUNCTIONS
# =========================
def generate_audio_from_script(
    script_text: str,
    sarvam_api_key: str,
    speaker: str = "arya",
    pitch: float = 0.0,
    pace: float = 1.0,
    loudness: float = 1.0,
    sample_rate: int = 22050,
    output_path: Optional[str] = None
) -> str:
    """Generate audio from Telugu script using Sarvam AI"""
    try:
        client = SarvamAI(api_subscription_key=sarvam_api_key)
        os.makedirs("temp_audio", exist_ok=True)
        
        raw_chunks = re.split(r'(?<=[।\.\?\!])\s+', script_text.strip())
        valid_chunks = [
            chunk for chunk in raw_chunks
            if len(chunk.strip()) > 3 and re.search(r'[\u0C00-\u0C7F]', chunk)
        ]
        
        if not valid_chunks:
            valid_chunks = [script_text]
        
        chunk_files = []
        
        for i, sentence in enumerate(valid_chunks):
            response = client.text_to_speech.convert(
                text=sentence,
                target_language_code="te-IN",
                speaker=speaker,
                pitch=pitch,
                pace=pace,
                loudness=loudness,
                output_audio_codec="mp3",
                speech_sample_rate=sample_rate,
                enable_preprocessing=True,
                model="bulbul:v2"
            )
            
            chunk_name = f"temp_audio/chunk_{i}.mp3"
            with open(chunk_name, "wb") as f:
                for audio_base64 in response.audios:
                    f.write(base64.b64decode(audio_base64))
            
            chunk_files.append(chunk_name)
        
        combined = AudioSegment.empty()
        for chunk in chunk_files:
            combined += AudioSegment.from_mp3(chunk)
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(get_output_base_path(), f"audio_output_{timestamp}.mp3")
        
        combined.export(output_path, format="mp3")
        
        for chunk in chunk_files:
            try:
                os.remove(chunk)
            except:
                pass
        try:
            os.rmdir("temp_audio")
        except:
            pass
        
        return output_path
        
    except Exception as e:
        raise RuntimeError(f"Audio generation failed: {str(e)}")


# =========================
# Telugu Number Conversion
# =========================
def convert_to_telugu_numbers(text: str) -> str:
    """Convert English numbers to Telugu numerals"""
    result = text
    for eng, tel in TELUGU_DIGITS.items():
        result = result.replace(eng, tel)
    return result.replace('...', '…')


def format_telugu_script(script: str) -> str:
    """Format Telugu script with proper numerals and news standards"""
    script = convert_to_telugu_numbers(script)
    script = script.replace('...', '…')
    return script


# =========================
# UTILITY FUNCTIONS
# =========================
def ensure_dirs():
    """Create necessary directories"""
    os.makedirs("output", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    try:
        ensure_output_base_exists()
    except:
        pass
    ensure_csv_exists()


def today_str():
    return datetime.now().strftime("%d %b %Y")


def make_client(api_key: str) -> OpenAI:
    """Create OpenAI client"""
    return OpenAI(api_key=api_key)


def get_optimal_model(source_type: str, commands: List[str], file_size_mb: float = 0) -> str:
    """Auto-select best model"""
    complex_scenarios = [
        source_type in ["image", "video"],
        "CRIME REPORT" in commands,
        "BREAKING NEWS" in commands,
        file_size_mb > 50,
        len(commands) >= 2,
    ]
    
    if any(complex_scenarios):
        return "gpt-4o"
    return "gpt-4o-mini"


def save_upload_to_temp(uploaded_file) -> str:
    """Save uploaded file to temp directory"""
    ensure_dirs()
    ext = os.path.splitext(uploaded_file.name)[1]
    path = os.path.join("temp", f"upload_{int(datetime.now().timestamp())}{ext}")
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def file_to_data_url(file_path: str) -> str:
    """Convert file to base64 data URL"""
    mime, _ = mimetypes.guess_type(file_path)
    if not mime:
        mime = "application/octet-stream"
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


# =========================
# VIDEO/AUDIO PROCESSING
# =========================
def create_silent_audio(output_path: str, duration: float = 1.0):
    """Create a silent audio file as fallback"""
    try:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "anullsrc=r=16000:cl=mono",
            "-t", str(duration),
            "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            "-loglevel", "error",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            raise Exception(f"Silent audio generation failed: {result.stderr}")
            
    except Exception:
        try:
            with wave.open(output_path, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(16000)
                silence = struct.pack('<h', 0) * 16000
                wav.writeframes(silence)
        except Exception as e:
            print(f"Failed to create silent audio: {e}")


def extract_audio_from_video(video_path: str, out_wav_path: str) -> None:
    """Extract audio using ffmpeg with robust error handling"""
    try:
        out_dir = os.path.dirname(out_wav_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_type",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)
        
        if probe_result.returncode != 0 or not probe_result.stdout.strip():
            create_silent_audio(out_wav_path, duration=1.0)
            raise RuntimeError("Video file has no audio stream")
        
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            "-loglevel", "error",
            out_wav_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg extraction failed: {result.stderr}")
        
        if not os.path.exists(out_wav_path) or os.path.getsize(out_wav_path) == 0:
            raise RuntimeError("Audio extraction produced empty file")
            
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg timeout - video processing took too long")
    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found. Please install ffmpeg and add to PATH")


def transcribe_audio(client: OpenAI, audio_path: str, language_hint: Optional[str] = None) -> str:
    """Transcribe audio using Whisper"""
    try:
        with open(audio_path, "rb") as f:
            resp = client.audio.transcriptions.create(
                model="whisper-1", file=f,
                language=language_hint, response_format="text"
            )
        return resp
    except Exception as e:
        raise RuntimeError(f"Transcription failed: {str(e)}")


def extract_frames_from_video(video_path: str, num_frames: int = 5) -> List[str]:
    """Extract key frames from video for analysis"""
    ensure_dirs()
    
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", video_path
    ]
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        duration = float(result.stdout.strip())
        
        frame_paths = []
        for i in range(num_frames):
            timestamp = (duration / (num_frames + 1)) * (i + 1)
            frame_path = os.path.join("temp", f"frame_{int(datetime.now().timestamp())}_{i}.jpg")
            
            cmd = [
                "ffmpeg", "-y", "-ss", str(timestamp), "-i", video_path,
                "-vframes", "1", "-q:v", "2", "-loglevel", "error", frame_path
            ]
            
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if os.path.exists(frame_path):
                frame_paths.append(frame_path)
        
        return frame_paths
    except Exception as e:
        raise RuntimeError(f"Failed to extract video frames: {str(e)}")


# Alias for compatibility
extract_video_frames = extract_frames_from_video


# =========================
# AI ANALYSIS
# =========================
def deep_analyze_image(client: OpenAI, image_data_url: str) -> str:
    """Deep AI analysis of image for news understanding"""
    analysis_prompt = """Analyze this image for TV news reporting.

Cover:
1. MAIN EVENT - What is happening?
2. PEOPLE - Who is visible?
3. LOCATION - Where is this?
4. NEWS ANGLE - What type of story?
5. KEY FACTS - Important details

Be detailed and specific."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": analysis_prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url, "detail": "high"}}
                ]
            }],
            max_tokens=2000,
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Image analysis failed: {str(e)}")


def deep_analyze_video(client: OpenAI, video_path: str) -> str:
    """Analyze video by extracting and analyzing frames"""
    try:
        frame_paths = extract_frames_from_video(video_path, num_frames=5)
        
        if not frame_paths:
            return "Unable to extract frames from video for analysis."
        
        content = [{"type": "text", "text": """Analyze these video frames for TV news.
Cover: NARRATIVE, PEOPLE, LOCATION, NEWS VALUE. Be detailed."""}]

        for i, frame_path in enumerate(frame_paths):
            content.append({"type": "text", "text": f"\nFrame {i+1}:"})
            content.append({"type": "image_url", "image_url": {
                "url": file_to_data_url(frame_path), "detail": "high"
            }})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": content}],
            max_tokens=2500, temperature=0.3
        )

        for frame in frame_paths:
            try:
                os.remove(frame)
            except:
                pass

        return response.choices[0].message.content
        
    except Exception as e:
        raise RuntimeError(f"Video analysis failed: {str(e)}")


def auto_detect_news_type(content: str, client: OpenAI) -> List[str]:
    """Auto-detect news type from content"""
    prompt = f"""Based on this content, return ONLY ONE news type from:
BREAKING NEWS, LIVE REPORT, HEADLINE NEWS, SPORTS NEWS, CRIME REPORT, POLITICAL NEWS, ENTERTAINMENT NEWS, HEALTH NEWS, BUSINESS NEWS, TECH NEWS, WEATHER REPORT

Content: {content[:1000]}

Return just the type name, nothing else."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a news editor who categorizes news stories."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50, temperature=0.1
        )
        detected = response.choices[0].message.content.strip()
        return [detected] if detected in TV_COMMAND_TYPES else ["HEADLINE NEWS"]
    except:
        return ["HEADLINE NEWS"]


# =========================
# SCRIPT GENERATION
# =========================
def get_tv_command_instructions(selected_commands: List[str]) -> str:
    """Generate TV-style instructions based on selected command types"""
    if not selected_commands:
        return ""
    
    instructions = []
    
    for cmd in selected_commands:
        if cmd in TV_COMMAND_TYPES:
            info = TV_COMMAND_TYPES[cmd]
            instructions.append(f"\n**{cmd} FORMAT:**")
            instructions.append(f"Sample Opening: \"{info['sample_opening']}\"")
            instructions.append(f"Voice Tone: {info['voice_tone']}")
            for inst in info.get("instructions", []):
                instructions.append(f"  • {inst}")
    
    return "\n".join(instructions)


def clean_script_output(script: str) -> str:
    """Clean and polish the news script"""
    skip_patterns = [
        '=', '---', '━', '─', '**', '##',
        'LANGUAGE:', 'SCRIPT START', 'SCRIPT END',
        '[PAUSE]', '[VISUAL', '[LOWER THIRD', '[B-ROLL',
        '[EMPHASIS', '[CUT TO', '[CAMERA',
        '📺', '🎯', '🤖', '📰', '🚨', '📡',
        'టీవీ న్యూస్',
        'TV NEWS SCRIPT', 'COMMAND:', 'AI-GENERATED'
    ]
    
    lines = script.split('\n')
    cleaned_lines = []
    
    for line in lines:
        if any(pattern in line for pattern in skip_patterns):
            continue
        
        line = re.sub(r'\[.*?\]', '', line)
        line = ' '.join(line.split())
        
        if line.strip() and len(line.strip()) > 5:
            cleaned_lines.append(line.strip())
    
    result = '\n\n'.join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    return result.strip()


# Alias for compatibility
clean_script = clean_script_output


def generate_tv_news_script_multilingual(
    client: OpenAI,
    model: str,
    source_type: str,
    command_types: List[str],
    languages: List[str],
    *,
    raw_text: Optional[str] = None,
    image_data_url: Optional[str] = None,
    video_path: Optional[str] = None,
    transcript: Optional[str] = None,
    content_analysis: Optional[str] = None,
    town: Optional[str] = None,
    incident_time: Optional[str] = None,
    **kwargs
) -> Dict[str, str]:
    """Generate Telugu TV news script"""

    main_command = command_types[0] if command_types else "HEADLINE NEWS"
    cmd_info = TV_COMMAND_TYPES.get(main_command, TV_COMMAND_TYPES["HEADLINE NEWS"])
    command_instructions = get_tv_command_instructions(command_types)

    system_prompt = f"""You are a professional Telugu TV news anchor writing a {main_command} script.

Sample Opening: "{cmd_info['sample_opening']}"
Voice Tone: {cmd_info['voice_tone']}

{command_instructions}

RULES:
1. Write EXACTLY what anchor says in Telugu
2. Natural conversational Telugu
3. ALL numbers in Telugu numerals (౦౧౨౩౪౫౬౭౮౯)
4. NO bullet points, headers, or technical markers
5. Continuous narrative only

Write ONLY the anchor's Telugu script."""

    parts = []
    if town or incident_time:
        ctx = []
        if town:
            ctx.append(f"Location: {town}")
        if incident_time:
            ctx.append(f"Time: {incident_time}")
        parts.append(f"CONTEXT: {', '.join(ctx)}\n")

    if content_analysis:
        parts.append(f"ANALYSIS:\n{content_analysis}\n")
    if transcript:
        parts.append(f"TRANSCRIPT:\n{transcript}\n")
    if raw_text:
        parts.append(f"INFO:\n{raw_text}\n")

    parts.append(f"Write complete Telugu {main_command} script now.")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "\n".join(parts)}
        ],
        temperature=0.5, max_tokens=3000
    )

    script = clean_script_output(response.choices[0].message.content)
    script = convert_to_telugu_numbers(script)

    return {"te": script}


def save_tv_script_output_multilingual(
    scripts: Dict[str, str],
    source_type: str,
    command_types: List[str]
) -> Dict[str, str]:
    """Save scripts to output folder"""
    output_folder = ensure_output_base_exists()
    timestamp = get_current_timestamp()

    prefix_map = {"image": "img", "video": "video", "audio": "audio", "text": "txt"}
    prefix = prefix_map.get(source_type, source_type)

    saved_paths = {}
    for lang, script in scripts.items():
        filename = f"{prefix}_output_{timestamp}.txt"
        path = os.path.join(output_folder, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(script)
        saved_paths[lang] = path

    return saved_paths


def display_tv_script_multilingual(scripts: Dict[str, str], command_types: List[str], model_used: str):
    """Display scripts in Streamlit"""
    import streamlit as st

    st.markdown(f"### 🤖 AI Model: `{model_used}`")

    if command_types and command_types[0] in TV_COMMAND_TYPES:
        info = TV_COMMAND_TYPES[command_types[0]]
        st.markdown(f"""
        <div style="background-color: {info['color']}20; border-left: 4px solid {info['color']};
                    padding: 15px; border-radius: 5px; margin: 10px 0;">
        <h3>{info['icon']} {command_types[0]}</h3>
        <p><strong>TV Style:</strong> {info.get('tv_style', command_types[0])}</p>
        <p><strong>Tone:</strong> {info['voice_tone']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    if "te" in scripts:
        st.markdown("### 🇮🇳 Telugu News Script")
        st.markdown(f"""
        <style>
        .telugu-script {{
            font-family: 'Nirmala UI', 'Gautami', sans-serif;
            font-size: 18px; line-height: 1.8;
            background-color: #f8f9fa; padding: 20px;
            border-radius: 8px; white-space: pre-wrap;
        }}
        </style>
        <div class="telugu-script">{scripts["te"]}</div>
        """, unsafe_allow_html=True)