# import os
# from datetime import datetime
# import streamlit as st
# from dotenv import load_dotenv

# from shared import (
#     TV_COMMAND_TYPES, make_client, ensure_dirs, get_output_base_path, VOICE_PRESETS
# )

# from video import process_video
# from audio import process_audio
# from image import process_image

# load_dotenv()
# ensure_dirs()


# def ensure_output_folders():
#     """Ensure 4 main folders exist: video, audio, image, text"""
#     base_path = get_output_base_path()
    
#     # Create only 4 folders - no subfolders
#     for folder in ['video', 'audio', 'image', 'text']:
#         os.makedirs(os.path.join(base_path, folder), exist_ok=True)
    
#     return base_path


# def get_next_file_number(folder_path, prefix):
#     """
#     Get the next available file number for a given prefix.
#     Example: If i1.txt, i2.txt exist, returns 3
#     """
#     if not os.path.exists(folder_path):
#         return 1
    
#     existing_files = os.listdir(folder_path)
#     numbers = []
    
#     for filename in existing_files:
#         # Match pattern like "i1.txt" or "v2.mp3"
#         if filename.startswith(prefix):
#             # Extract number after prefix
#             try:
#                 # Remove extension and get number
#                 name_without_ext = os.path.splitext(filename)[0]
#                 num_part = name_without_ext[len(prefix):]
#                 if num_part.isdigit():
#                     numbers.append(int(num_part))
#             except:
#                 continue
    
#     if not numbers:
#         return 1
    
#     return max(numbers) + 1


# def categorize_uploads(uploaded_files):
#     """Categorize files by type"""
#     categories = {'video': [], 'audio': [], 'image': []}
    
#     video_exts = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
#     audio_exts = {'.mp3', '.wav', '.m4a', '.ogg', '.flac'}
#     image_exts = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    
#     for file in uploaded_files:
#         ext = os.path.splitext(file.name)[1].lower()
        
#         if ext in video_exts:
#             categories['video'].append(file)
#         elif ext in audio_exts:
#             categories['audio'].append(file)
#         elif ext in image_exts:
#             categories['image'].append(file)
    
#     return categories


# def main():
#     st.set_page_config(
#         page_title="Telugu News Script + TTS Generator",
#         layout="wide",
#         page_icon="📺"
#     )
    
#     st.title("📺 Telugu TV News Script + Audio Generator")
#     st.caption("Upload Media → AI Generates Script → Convert to Speech")
    
#     with st.sidebar:
#         st.header("⚙️ Configuration")
        
#         st.subheader("🔐 API Keys")
#         openai_key = st.text_input(
#             "OpenAI API Key",
#             value=os.getenv("OPENAI_API_KEY", ""),
#             type="password"
#         )
        
#         sarvam_key = st.text_input(
#             "Sarvam AI Key (for TTS)",
#             value=os.getenv("SARVAM_API_KEY", ""),
#             type="password",
#             help="Required for audio generation"
#         )
        
#         st.divider()
        
#         st.subheader("🎙️ Text-to-Speech Settings")
#         enable_tts = st.checkbox("Generate Audio Output", value=True, help="Convert scripts to speech")
        
#         if enable_tts:
#             st.markdown("**Select News Anchor Voice:**")
            
#             speaker = st.selectbox(
#                 "Anchor Voice",
#                 options=list(VOICE_PRESETS.keys()),
#                 format_func=lambda x: f"{VOICE_PRESETS[x]['name']} ({VOICE_PRESETS[x]['gender']}) - {VOICE_PRESETS[x]['style']}",
#                 index=3
#             )
            
#             voice_info = VOICE_PRESETS[speaker]
#             st.info(f"🎤 **{voice_info['name']}** - {voice_info['style']}")
            
#             with st.expander("🎚️ Advanced Voice Controls"):
#                 pitch = st.slider("Pitch", -1.0, 1.0, 0.0, 0.1)
#                 pace = st.slider("Pace", 0.5, 2.0, 1.0, 0.1)
#                 loudness = st.slider("Loudness", 0.5, 2.0, 1.0, 0.1)
#                 sample_rate = st.selectbox("Sample Rate", [8000, 16000, 22050, 44100], index=2)
            
#             voice_settings = {
#                 'speaker': speaker,
#                 'pitch': pitch,
#                 'pace': pace,
#                 'loudness': loudness,
#                 'sample_rate': sample_rate
#             }
#         else:
#             voice_settings = None
        
#         st.divider()
        
#         st.subheader("🎬 News Format")
#         manual_command = st.selectbox(
#             "Format:",
#             ["AUTO-DETECT"] + list(TV_COMMAND_TYPES.keys()),
#             format_func=lambda x: f"🤖 {x}" if x == "AUTO-DETECT" 
#                                   else f"{TV_COMMAND_TYPES[x]['icon']} {x}"
#         )
        
#         st.divider()
        
#         lang_hint = st.selectbox("🎤 Speech Language", ["auto", "te", "en", "hi"])
        
#         st.subheader("📍 Context (Optional)")
#         town = st.text_input("Location", placeholder="e.g., హైదరాబాద్")
#         incident_time = st.text_input("Time", placeholder="e.g., ఈ ఉదయం")
        
#         st.divider()
#         st.info(f"📂 **Output:** `{get_output_base_path()}`")
    
#     st.markdown("### 📤 Upload Media Files")
    
#     if enable_tts and sarvam_key:
#         st.success(f"🎙️ TTS Enabled with **{VOICE_PRESETS[voice_settings['speaker']]['name']}** voice")
#     elif enable_tts and not sarvam_key:
#         st.warning("⚠️ TTS enabled but Sarvam AI key missing - scripts will be generated without audio")
    
#     uploaded_files = st.file_uploader(
#         "Upload Video/Audio/Image Files",
#         type=["mp4", "mov", "avi", "mkv", "webm", "mp3", "wav", "m4a", "ogg", "flac", "jpg", "jpeg", "png", "webp", "gif"],
#         accept_multiple_files=True
#     )
    
#     if uploaded_files:
#         categories = categorize_uploads(uploaded_files)
        
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             st.metric("🎥 Videos", len(categories['video']))
#             if categories['video']:
#                 for f in categories['video']:
#                     st.caption(f"• {f.name}")
        
#         with col2:
#             st.metric("🎤 Audio", len(categories['audio']))
#             if categories['audio']:
#                 for f in categories['audio']:
#                     st.caption(f"• {f.name}")
        
#         with col3:
#             st.metric("📸 Images", len(categories['image']))
#             if categories['image']:
#                 for f in categories['image']:
#                     st.caption(f"• {f.name}")
        
#         st.divider()
        
#         total_files = len(uploaded_files)
#         can_process = openai_key.strip() and total_files > 0
        
#         if enable_tts and not sarvam_key:
#             button_text = f"⚠️ PROCESS {total_files} FILE(S) (Text Only - No Audio)"
#         elif enable_tts:
#             button_text = f"🚀 PROCESS {total_files} FILE(S) → GENERATE SCRIPTS + AUDIO"
#         else:
#             button_text = f"🚀 PROCESS {total_files} FILE(S) → GENERATE SCRIPTS"
        
#         if st.button(button_text, disabled=not can_process, type="primary", use_container_width=True):
#             process_all_media(
#                 categories, openai_key, manual_command,
#                 lang_hint, town, incident_time,
#                 enable_tts, sarvam_key, voice_settings
#             )
#     else:
#         st.info("👆 Upload one or more media files to begin")
    
#     st.markdown("---")
#     st.caption("📺 Telugu Multi-Media News Script + Audio Generator")


# def process_all_media(categories, openai_key, manual_command, lang_hint, town, incident_time,
#                      enable_tts, sarvam_key, voice_settings):
#     """Process all uploaded media"""
    
#     output_base = ensure_output_folders()
#     st.success(f"📁 Output directory: `{output_base}`")
    
#     client = make_client(openai_key.strip())
    
#     total_files = sum(len(files) for files in categories.values())
#     processed = 0
    
#     overall_progress = st.progress(0)
#     overall_status = st.empty()
    
#     all_results = []
    
#     can_generate_audio = enable_tts and sarvam_key and sarvam_key.strip()
    
#     if categories['video']:
#         st.markdown("---")
#         st.markdown("### 🎥 Processing Videos")
        
#         # Get video folder for numbering
#         video_folder = os.path.join(output_base, "video")
#         start_num = get_next_file_number(video_folder, "v")
        
#         for idx, video_file in enumerate(categories['video']):
#             file_num = start_num + idx
#             overall_status.text(f"Processing video {idx+1}/{len(categories['video'])}: {video_file.name}")
            
#             # Simple prefix: v1, v2, v3...
#             file_prefix = f"v{file_num}"
            
#             with st.expander(f"🎥 Video {idx+1}: {video_file.name}", expanded=True):
#                 try:
#                     result = process_video(
#                         video_file, client, manual_command,
#                         lang_hint, town, incident_time,
#                         output_base=output_base,
#                         file_prefix=file_prefix,
#                         generate_audio=can_generate_audio,
#                         sarvam_api_key=sarvam_key if can_generate_audio else None,
#                         voice_settings=voice_settings if can_generate_audio else None
#                     )
#                     all_results.append(result)
#                     st.success(f"✅ Video {idx+1} processed → {file_prefix}")
#                 except Exception as e:
#                     st.error(f"❌ Failed: {str(e)}")
            
#             processed += 1
#             overall_progress.progress(processed / total_files)
    
#     if categories['audio']:
#         st.markdown("---")
#         st.markdown("### 🎤 Processing Audio Files")
        
#         # Get audio folder for numbering
#         audio_folder = os.path.join(output_base, "audio")
#         start_num = get_next_file_number(audio_folder, "a")
        
#         for idx, audio_file in enumerate(categories['audio']):
#             file_num = start_num + idx
#             overall_status.text(f"Processing audio {idx+1}/{len(categories['audio'])}: {audio_file.name}")
            
#             # Simple prefix: a1, a2, a3...
#             file_prefix = f"a{file_num}"
            
#             with st.expander(f"🎤 Audio {idx+1}: {audio_file.name}", expanded=True):
#                 try:
#                     result = process_audio(
#                         audio_file, client, manual_command,
#                         lang_hint, town, incident_time,
#                         output_base=output_base,
#                         file_prefix=file_prefix,
#                         generate_audio=can_generate_audio,
#                         sarvam_api_key=sarvam_key if can_generate_audio else None,
#                         voice_settings=voice_settings if can_generate_audio else None
#                     )
#                     all_results.append(result)
#                     st.success(f"✅ Audio {idx+1} processed → {file_prefix}")
#                 except Exception as e:
#                     st.error(f"❌ Failed: {str(e)}")
            
#             processed += 1
#             overall_progress.progress(processed / total_files)
    
#     if categories['image']:
#         st.markdown("---")
#         st.markdown("### 📸 Processing Images")
        
#         # Get image folder for numbering
#         image_folder = os.path.join(output_base, "image")
#         start_num = get_next_file_number(image_folder, "i")
        
#         for idx, image_file in enumerate(categories['image']):
#             file_num = start_num + idx
#             overall_status.text(f"Processing image {idx+1}/{len(categories['image'])}: {image_file.name}")
            
#             # Simple prefix: i1, i2, i3...
#             file_prefix = f"i{file_num}"
            
#             with st.expander(f"📸 Image {idx+1}: {image_file.name}", expanded=True):
#                 try:
#                     result = process_image(
#                         image_file, client, manual_command,
#                         town, incident_time,
#                         output_base=output_base,
#                         file_prefix=file_prefix,
#                         generate_audio=can_generate_audio,
#                         sarvam_api_key=sarvam_key if can_generate_audio else None,
#                         voice_settings=voice_settings if can_generate_audio else None
#                     )
#                     all_results.append(result)
#                     st.success(f"✅ Image {idx+1} processed → {file_prefix}")
#                 except Exception as e:
#                     st.error(f"❌ Failed: {str(e)}")
            
#             processed += 1
#             overall_progress.progress(processed / total_files)
    
#     overall_progress.progress(1.0)
#     overall_status.text("✅ All files processed!")
    
#     st.markdown("---")
#     st.markdown("### 📊 Processing Summary")
    
#     success_count = len([r for r in all_results if r.get('status') == 'SUCCESS'])
#     audio_count = len([r for r in all_results if r.get('audio_file')])
    
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         st.metric("Total Files", total_files)
#     with col2:
#         st.metric("Successful", success_count)
#     with col3:
#         st.metric("Scripts", success_count)
#     with col4:
#         st.metric("Audio Files", audio_count)
    
#     st.success(f"### ✅ All outputs saved to: `{output_base}`")
    
#     st.markdown("#### 📂 Output Structure:")
#     st.code(f"""{output_base}/
# ├── video/     (Video files: v1.mp4, v2.mp4, ...)
# ├── audio/     (Audio files: a1.mp3, a2.mp3, ...)
# ├── image/     (Image files: i1.jpg, i2.jpg, ...)
# └── text/      (Text scripts: v1.txt, a1.txt, i1.txt, ...)""")
    
#     with st.expander("📂 View All Generated Files"):
#         for result in all_results:
#             if result.get('output_file'):
#                 st.text(f"📄 {result['output_file']}")
#             if result.get('audio_file'):
#                 st.text(f"🔊 {result['audio_file']}")


# if __name__ == "__main__":
#     main()





















from moderation import run_moderation
from dup import check_duplicate
from sum import summarize
from text_processor import generate_script
from audio import generate_audio
from video import generate_video
from vision_processor import generate_images


def run_pipeline(input_text, voice_settings):
    text = run_moderation(input_text)

    if check_duplicate(text):
        return "Duplicate skipped"

    summary = summarize(text)
    script = generate_script(summary)

    audio_path = generate_audio(script, voice_settings)
    images = generate_images(script)
    video_path = generate_video(script, audio_path)

    return {
        "script": script,
        "audio": audio_path,
        "video": video_path,
        "images": images
    }


if __name__ == "__main__":
    run_pipeline("Sample News Input", {})
