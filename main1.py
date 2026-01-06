import os
import tempfile
import subprocess
import time
import base64
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from elevenlabs.client import ElevenLabs

load_dotenv()

# ---------------- SETUP ----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not OPENAI_API_KEY or not ELEVENLABS_API_KEY:
    raise RuntimeError("Missing API keys")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "kn": "Kannada",
}


# ---------------- RETRY ----------------
def openai_retry(call, retries=5, delay=0.5):
    for i in range(retries):
        try:
            return call()
        except RateLimitError:
            if i == retries - 1:
                raise
            time.sleep(delay * (2 ** i))


# ---------------- FILE TYPE ----------------
def is_video(p): return p.lower().endswith((".mp4", ".mkv", ".mov", ".avi", ".webm"))
def is_audio(p): return p.lower().endswith((".wav", ".mp3", ".m4a", ".ogg"))
def is_image(p): return p.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))


# ---------------- FFmpeg ----------------
def extract_audio(video_path):
    audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000", audio_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return audio_path
    except:
        return None


def extract_frames(video_path):
    frame_dir = tempfile.mkdtemp()
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-vf", "fps=1/2,scale=640:-1", f"{frame_dir}/f_%02d.jpg"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return [os.path.join(frame_dir, f) for f in os.listdir(frame_dir)][:5]


# ---------------- STT ----------------
def transcribe_audio(audio_path):
    with open(audio_path, "rb") as f:
        return openai_client.audio.transcriptions.create(
            file=f,
            model="whisper-1",
            response_format="text"
        )


# ---------------- VISION ----------------
def analyze_images(images):
    content = [{"type": "text", "text": "Describe this like a TV news reporter."}]
    for img in images:
        with open(img, "rb") as f:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
                }
            })

    resp = openai_retry(lambda: openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content}],
        max_tokens=400,
        temperature=0.2
    ))
    return resp.choices[0].message.content.strip()


# ---------------- NEWS SCRIPT ----------------
def generate_news_script(text, lang="en"):
    language = LANGUAGE_MAP.get(lang, "English")
    resp = openai_retry(lambda: openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You are a TV news anchor writing in {language}."},
            {"role": "user", "content": text}
        ],
        max_tokens=700,
        temperature=0.3
    ))
    return resp.choices[0].message.content.strip()


# ---------------- CHAT ----------------
def llm_chat_reply(user_text):
    resp = openai_retry(lambda: openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Reply briefly like a WhatsApp bot."},
            {"role": "user", "content": user_text}
        ],
        max_tokens=100
    ))
    return resp.choices[0].message.content.strip()


# ---------------- TTS ----------------
def text_to_speech(text):
    output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    audio = elevenlabs_client.text_to_speech.convert(
        text=text,
        voice_id="21m00Tcm4TlvDq8ikWAM",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128"
    )
    with open(output, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    return output


# ---------------- PIPELINE ----------------
def process_file(file_path, lang="en"):
    if is_video(file_path):
        audio = extract_audio(file_path)
        transcript = transcribe_audio(audio) if audio else "[No audio]"
        visuals = analyze_images(extract_frames(file_path))
        content = f"{visuals}\n\nAudio: {transcript}"

    elif is_audio(file_path):
        content = transcribe_audio(file_path)

    elif is_image(file_path):
        content = analyze_images([file_path])

    else:
        return {"error": "Unsupported format"}

    script = generate_news_script(content, lang)
    audio_out = text_to_speech(script)

    return {
        "success": True,
        "news_script": script,
        "audio_path": audio_out
    }
