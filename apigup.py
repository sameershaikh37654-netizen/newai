import os
import json
import requests
from flask import Flask, request
from dotenv import load_dotenv
from datetime import datetime
import mimetypes

# import the LLM/chat helper and file processor
from main1 import llm_chat_reply, process_file

load_dotenv()

app = Flask(__name__)

# ================= CONFIG =================
GUPSHUP_API_KEY = os.getenv("GUPSHUP_API_KEY")
GUPSHUP_SOURCE_NUMBER = os.getenv("GUPSHUP_SOURCE_NUMBER")  # 91XXXXXXXXXX
GUPSHUP_APP_NAME = os.getenv("GUPSHUP_APP_NAME", "lastnumber")

GUPSHUP_SEND_URL = "https://api.gupshup.io/wa/api/v1/msg"

# Create media directory if it doesn't exist
MEDIA_DIR = "downloaded_media"
os.makedirs(MEDIA_DIR, exist_ok=True)
# =========================================

if not GUPSHUP_API_KEY or not GUPSHUP_SOURCE_NUMBER:
    raise RuntimeError("Please set GUPSHUP_API_KEY and GUPSHUP_SOURCE_NUMBER in .env")


# =====================================================
# DOWNLOAD MEDIA FILE
# =====================================================
def download_media(media_url, msg_type, sender):
    """
    Download media from WhatsApp URL
    Returns: local file path or None
    """
    try:
        print(f"🔽 Downloading {msg_type} from: {media_url}")
        
        # Set headers (Gupshup may require API key for media download)
        headers = {
            "apikey": GUPSHUP_API_KEY,
            "User-Agent": "Mozilla/5.0"
        }
        
        # Download the file
        response = requests.get(media_url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # Get file extension from content-type or URL
        content_type = response.headers.get('content-type', '')
        extension = mimetypes.guess_extension(content_type.split(';')[0])
        
        if not extension:
            # Fallback: extract from URL or use msg_type
            if '.' in media_url.split('/')[-1]:
                extension = '.' + media_url.split('.')[-1].split('?')[0]
            else:
                extension_map = {
                    'image': '.jpg',
                    'video': '.mp4',
                    'audio': '.mp3',
                    'document': '.pdf',
                    'voice': '.ogg'
                }
                extension = extension_map.get(msg_type, '.bin')
        
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_sender = sender.replace('+', '').replace(' ', '')
        filename = f"{safe_sender}_{timestamp}_{msg_type}{extension}"
        filepath = os.path.join(MEDIA_DIR, filename)
        
        # Save file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = os.path.getsize(filepath)
        print(f"✅ Downloaded: {filename} ({file_size} bytes)")
        
        return filepath
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Download failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return None


# =====================================================
# SEND NORMAL WHATSAPP MESSAGE
# =====================================================
def send_whatsapp_message(destination, message_text):
    headers = {
        "apikey": GUPSHUP_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "channel": "whatsapp",
        "source": GUPSHUP_SOURCE_NUMBER,
        "destination": destination,
        "src.name": GUPSHUP_APP_NAME,
        "message": json.dumps({
            "type": "text",
            "text": message_text
        })
    }

    try:
        r = requests.post(GUPSHUP_SEND_URL, headers=headers, data=payload, timeout=15)
        print("📤 SEND STATUS:", r.status_code, r.text)
        return r.status_code, r.text
    except Exception as e:
        print("❌ Send Error:", e)
        return None, str(e)


# =====================================================
# SEND TEMPLATE MESSAGE (SESSION CLOSED)
# =====================================================
def send_template_message(destination, template_id, template_params=None):
    headers = {
        "apikey": GUPSHUP_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "channel": "whatsapp",
        "source": GUPSHUP_SOURCE_NUMBER,
        "destination": destination,
        "src.name": GUPSHUP_APP_NAME,
        "message": json.dumps({
            "type": "template",
            "template": {
                "id": template_id,
                "params": template_params or []
            }
        })
    }

    try:
        r = requests.post(GUPSHUP_SEND_URL, headers=headers, data=payload, timeout=15)
        print("📤 TEMPLATE STATUS:", r.status_code, r.text)
        return r.status_code, r.text
    except Exception as e:
        print("❌ Template Error:", e)
        return None, str(e)


# =====================================================
# GUPSHUP WEBHOOK (WITH AUTO MEDIA DOWNLOAD)
# =====================================================
@app.route("/gupshup/webhook", methods=["POST", "GET"])
def gupshup_webhook():
    if request.method == "GET":
        return "OK", 200

    try:
        data = request.get_json(force=True)
    except Exception as e:
        print("❌ Invalid JSON:", e)
        return "OK", 200

    # 🔥 LOG EVERYTHING
    print("\n============= GUPSHUP EVENT =============")
    print(json.dumps(data, indent=2))
    print("========================================\n")

    event_type = data.get("type")

    # =================================================
    # ❌ DELIVERY FAILURE CALLBACK
    # =================================================
    if event_type == "failed":
        payload = data.get("payload", {})
        print("❌ MESSAGE FAILED")
        print("To:", payload.get("destination"))
        print("Error Code:", payload.get("code"))
        print("Reason:", payload.get("reason"))
        return "OK", 200

    # =================================================
    # IGNORE NON-MESSAGE EVENTS
    # =================================================
    if event_type != "message":
        print("ℹ️ Ignored event:", event_type)
        return "OK", 200

    payload = data.get("payload", {}) or {}
    sender = payload.get("source") or (payload.get("sender") or {}).get("phone")
    msg_type = payload.get("type")

    if not sender or not msg_type:
        print("⚠️ Missing sender or message type")
        return "OK", 200

    # ================= TEXT MESSAGE =================
    if msg_type == "text":
        incoming_text = payload.get("payload", {}).get("text", "").strip()
        print("📩 USER TEXT:", incoming_text)

        reply_text = llm_chat_reply(incoming_text) or \
                     "Sorry, something went wrong. Please try again."

        send_whatsapp_message(sender, reply_text)

    # ================= MEDIA MESSAGE =================
    elif msg_type in ["image", "video", "audio", "document", "voice", "sticker"]:
        print(f"📎 Received {msg_type} from {sender}")
        
        # Notify user
        send_whatsapp_message(sender, f"📩 {msg_type.capitalize()} received. Downloading...")

        media_payload = payload.get("payload", {})
        
        # Try different possible field names for media URL
        media_url = (
            media_payload.get("url")
            or media_payload.get("mediaUrl")
            or media_payload.get("fileUrl")
            or media_payload.get("link")
        )
        
        # Get caption if available
        caption = media_payload.get("caption", "")

        if media_url:
            # Download the media file
            local_path = download_media(media_url, msg_type, sender)
            
            if local_path:
                # Process the file with your LLM
                try:
                    result = process_file(local_path)
                    
                    if result:
                        response_text = f"✅ {msg_type.capitalize()} processed successfully!\n\n{result}"
                    else:
                        response_text = f"✅ {msg_type.capitalize()} downloaded and saved: {os.path.basename(local_path)}"
                    
                    if caption:
                        response_text += f"\n\nCaption: {caption}"
                    
                    send_whatsapp_message(sender, response_text)
                    
                except Exception as e:
                    print(f"❌ Processing error: {e}")
                    send_whatsapp_message(sender, f"✅ {msg_type.capitalize()} downloaded but processing failed. File saved: {os.path.basename(local_path)}")
            else:
                send_whatsapp_message(sender, f"❌ Failed to download {msg_type}. Please try again.")
        else:
            print(f"⚠️ {msg_type} received but no URL found")
            send_whatsapp_message(sender, f"⚠️ Received {msg_type} but couldn't find download link.")
    
    # ================= LOCATION =================
    elif msg_type == "location":
        location_payload = payload.get("payload", {})
        latitude = location_payload.get("latitude")
        longitude = location_payload.get("longitude")
        print(f"📍 Location received: {latitude}, {longitude}")
        send_whatsapp_message(sender, f"📍 Location received: {latitude}, {longitude}")
    
    # ================= CONTACT =================
    elif msg_type == "contact":
        print("👤 Contact card received")
        send_whatsapp_message(sender, "👤 Contact card received!")
    
    # ================= OTHER =================
    else:
        print(f"⚠️ Unsupported message type: {msg_type}")
        send_whatsapp_message(sender, "⚠️ This message type is not supported yet.")

    return "OK", 200


# =====================================================
# META WEBHOOK (SAFE NO-OP)
# =====================================================
@app.route("/whatsapp/webhook", methods=["POST", "GET"])
def meta_webhook():
    return "OK", 200


# =====================================================
# HEALTH CHECK
# =====================================================
@app.route("/health", methods=["GET"])
def health_check():
    return {"status": "ok", "media_dir": MEDIA_DIR}, 200


# =====================================================
# RUN APP
# =====================================================
if __name__ == "__main__":
    print(f"📁 Media will be saved to: {os.path.abspath(MEDIA_DIR)}")
    app.run(host="0.0.0.0", port=8000, debug=True)