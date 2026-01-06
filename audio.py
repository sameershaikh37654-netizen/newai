import os
from datetime import datetime
import streamlit as st

from shared import (
    save_upload_to_temp, transcribe_audio, auto_detect_news_type, get_optimal_model,
    generate_tv_news_script_multilingual, log_to_csv,
    generate_audio_from_script, VOICE_PRESETS
)


def process_audio(audio_file, client, manual_command, lang_hint, town, incident_time,
                 output_base=None, file_prefix="a1",
                 generate_audio=False, sarvam_api_key=None, voice_settings=None):
    
    file_size_mb = audio_file.size / (1024 * 1024)
    progress = st.progress(0)
    status = st.empty()
    
    try:
        status.text("🎤 Transcribing audio...")
        progress.progress(30)
        
        audio_path = save_upload_to_temp(audio_file)
        lang = None if lang_hint == "auto" else lang_hint
        transcript = transcribe_audio(client, audio_path, lang)
        
        st.success("✓ Audio transcribed")
        progress.progress(60)
        
        with st.expander("📋 View Transcript"):
            st.text_area("Transcript:", transcript, height=150, key=f"transcript_{file_prefix}")
        
        if manual_command == "AUTO-DETECT":
            status.text("🤖 Detecting news type...")
            selected_commands = auto_detect_news_type(transcript, client)
            st.info(f"Detected: {selected_commands[0]}")
        else:
            selected_commands = [manual_command]
        
        progress.progress(70)
        
        status.text("📺 Creating Telugu script...")
        model = get_optimal_model("audio", selected_commands, file_size_mb)
        
        scripts = generate_tv_news_script_multilingual(
            client=client, model=model,
            source_type="audio",
            command_types=selected_commands,
            languages=["te"],
            transcript=transcript,
            content_analysis=f"Audio transcript:\n{transcript}",
            town=town or None,
            incident_time=incident_time or None
        )
        
        progress.progress(90)
        
        status.text("💾 Saving files...")
        
        if output_base:
            # Save original audio to audio folder
            audio_folder = os.path.join(output_base, "audio")
            os.makedirs(audio_folder, exist_ok=True)
            
            audio_ext = os.path.splitext(audio_file.name)[1]
            audio_output_filename = f"{file_prefix}_original{audio_ext}"
            audio_input_path = os.path.join(audio_folder, audio_output_filename)
            
            # Copy the audio file
            with open(audio_path, "rb") as src, open(audio_input_path, "wb") as dst:
                dst.write(src.read())
            
            # Save text script to text folder
            text_folder = os.path.join(output_base, "text")
            os.makedirs(text_folder, exist_ok=True)
            
            text_output_filename = f"{file_prefix}.txt"
            text_output_path = os.path.join(text_folder, text_output_filename)
            
            with open(text_output_path, "w", encoding="utf-8") as f:
                f.write(scripts["te"])
        else:
            from shared import save_tv_script_output_multilingual
            script_paths = save_tv_script_output_multilingual(scripts, "audio", selected_commands)
            text_output_path = script_paths["te"]
            audio_input_path = None
        
        tts_audio_path = None
        if generate_audio and sarvam_api_key:
            try:
                status.text("🎙️ Generating TTS audio...")
                progress.progress(95)
                
                voice_settings = voice_settings or {}
                speaker = voice_settings.get('speaker', 'arya')
                pitch = voice_settings.get('pitch', 0.0)
                pace = voice_settings.get('pace', 1.0)
                loudness = voice_settings.get('loudness', 1.0)
                sample_rate = voice_settings.get('sample_rate', 22050)
                
                if output_base:
                    # Save TTS audio to audio folder
                    audio_folder = os.path.join(output_base, "audio")
                    os.makedirs(audio_folder, exist_ok=True)
                    
                    tts_filename = f"{file_prefix}.mp3"
                    tts_audio_path = os.path.join(audio_folder, tts_filename)
                else:
                    tts_audio_path = None
                
                tts_audio_path = generate_audio_from_script(
                    script_text=scripts["te"],
                    sarvam_api_key=sarvam_api_key,
                    speaker=speaker,
                    pitch=pitch,
                    pace=pace,
                    loudness=loudness,
                    sample_rate=sample_rate,
                    output_path=tts_audio_path
                )
                
                st.success(f"✅ TTS audio generated with {VOICE_PRESETS[speaker]['name']} voice!")
                
            except Exception as e:
                error_msg = str(e)
                if "Subscription not found" in error_msg or "403" in error_msg:
                    st.warning("⚠️ TTS generation failed: Invalid or expired Sarvam AI API key.")
                else:
                    st.warning(f"⚠️ TTS generation failed: {error_msg}")
                tts_audio_path = None
        
        progress.progress(100)
        status.text("✅ Complete!")
        
        st.markdown("**📺 Generated Telugu Script:**")
        st.markdown(f"""
        <div style="font-family: 'Nirmala UI', 'Gautami', sans-serif; font-size: 16px;
                    background-color: #f8f9fa; padding: 15px; border-radius: 8px;">
        {scripts["te"]}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with open(text_output_path, "rb") as f:
                st.download_button(
                    "📥 Download Script (TXT)",
                    data=f,
                    file_name=os.path.basename(text_output_path),
                    mime="text/plain",
                    key=f"download_txt_{file_prefix}"
                )
        
        if audio_input_path and os.path.exists(audio_input_path):
            with col2:
                st.info(f"🎵 Input audio saved: {os.path.basename(audio_input_path)}")
        
        if tts_audio_path and os.path.exists(tts_audio_path):
            with col3:
                with open(tts_audio_path, "rb") as f:
                    st.download_button(
                        "📥 Download TTS Audio (MP3)",
                        data=f,
                        file_name=os.path.basename(tts_audio_path),
                        mime="audio/mp3",
                        key=f"download_audio_{file_prefix}"
                    )
            
            st.markdown("### 🔊 Listen to Generated TTS Audio")
            with open(tts_audio_path, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
        
        output_files = [text_output_path]
        if audio_input_path:
            output_files.append(audio_input_path)
        if tts_audio_path:
            output_files.append(tts_audio_path)
        
        try:
            log_to_csv(
                source_type="AUDIO",
                input_file_name=audio_file.name,
                input_file_size_mb=file_size_mb,
                languages=["te"],
                news_format=selected_commands[0],
                location=town,
                incident_time=incident_time,
                ai_model=model,
                output_files=output_files,
                audio_generated=tts_audio_path is not None,
                status="SUCCESS",
                notes=f"Prefix: {file_prefix}, Lang: {lang_hint}"
            )
        except Exception as log_error:
            st.warning(f"Could not log to CSV: {log_error}")
        
        return {
            'status': 'SUCCESS',
            'output_file': text_output_path,
            'input_audio_file': audio_input_path,
            'audio_file': tts_audio_path,
            'news_format': selected_commands[0],
            'model': model
        }
        
    except Exception as e:
        status.text("❌ Failed")
        st.error(f"Error: {str(e)}")
        
        try:
            log_to_csv(
                source_type="AUDIO",
                input_file_name=audio_file.name,
                input_file_size_mb=file_size_mb,
                languages=["te"],
                news_format="ERROR",
                location=town,
                incident_time=incident_time,
                ai_model="N/A",
                output_files=[],
                audio_generated=False,
                status="FAILED",
                notes=f"Error: {str(e)}"
            )
        except:
            pass
        
        return {
            'status': 'FAILED',
            'error': str(e)
        }










































# import os
# from datetime import datetime
# from typing import List, Dict, Optional
# import streamlit as st
# from dotenv import load_dotenv
# from openai import OpenAI

# from shared import (
#     TV_COMMAND_TYPES, get_tv_command_instructions, get_optimal_model,
#     ensure_dirs, save_upload_to_temp, make_client,
#     transcribe_audio, auto_detect_news_type,
#     generate_tv_news_script_multilingual,
#     save_tv_script_output_multilingual, display_tv_script_multilingual,
#     log_to_csv
# )

# load_dotenv()
# ensure_dirs()

# def main():
#     st.set_page_config(
#         page_title="AI TV News Script Generator - Audio (Telugu)",
#         layout="wide",
#         page_icon="🎤"
#     )
    
#     st.title("🎤 AI-Powered TV News Script Generator - Audio")
#     st.caption("Upload Audio → AI Transcribes & Analyzes → Generates Professional Telugu Broadcast Scripts")
    
#     with st.sidebar:
#         st.header("⚙️ Configuration")
        
#         st.subheader("🔐 OpenAI API Key")
#         env_key = os.getenv("OPENAI_API_KEY", "")
#         api_key = st.text_input("API Key", value=env_key, type="password")
        
#         st.info("""
#         **✨ Features for Audio:**
#         - Speech-to-text transcription
#         - Content analysis
#         - Professional Telugu broadcast scripts
#         """)
        
#         st.divider()
        
#         st.subheader("🌐 Output Language")
#         st.success("🇮🇳 **Telugu Only**")
#         languages = ["te"]
        
#         st.divider()
        
#         st.subheader("🎬 News Format")
#         manual_command = st.selectbox(
#             "Manual override:",
#             options=["AUTO-DETECT"] + list(TV_COMMAND_TYPES.keys()),
#             format_func=lambda x: f"🤖 {x}" if x == "AUTO-DETECT" else f"{TV_COMMAND_TYPES[x]['icon']} {x}"
#         )
        
#         st.divider()
        
#         st.subheader("🎤 Audio Language Hint")
#         lang_hint = st.selectbox(
#             "Speech Language",
#             ["auto", "te", "en", "hi", "kn", "ta", "mr"],
#             index=0
#         )
        
#         st.subheader("📍 Additional Context")
#         town = st.text_input("Location", placeholder="e.g., Hyderabad")
#         incident_time = st.text_input("Time", placeholder="e.g., ఈ ఉదయం")
        
#         st.divider()
#         st.info("**📂 Output:** `C:\\Users\\GLOBAL T\\Desktop\\output\\`")
    
#     st.markdown("### 🎤 Upload News Audio")
    
#     col1, col2 = st.columns([1, 1])
    
#     with col1:
#         uploaded = st.file_uploader(
#             "Upload Audio",
#             type=["mp3", "wav", "m4a", "ogg", "flac"]
#         )
        
#         if uploaded:
#             file_size = uploaded.size / (1024 * 1024)
#             st.success(f"✓ Audio uploaded ({file_size:.1f} MB)")
#             st.audio(uploaded)
    
#     with col2:
#         st.markdown("### 🚀 Generate Telugu Script")
#         st.info("**Output:** 🇮🇳 Telugu Script Only")
        
#         can_generate = api_key.strip() and uploaded
        
#         generate_btn = st.button(
#             "🎤 GENERATE TELUGU BROADCAST SCRIPT",
#             use_container_width=True,
#             type="primary",
#             disabled=not can_generate
#         )
    
#     if generate_btn:
#         client = make_client(api_key.strip())
#         file_size_mb = uploaded.size / (1024 * 1024)
        
#         progress_bar = st.progress(0)
#         status_text = st.empty()
        
#         try:
#             status_text.text("🔄 Processing audio...")
#             progress_bar.progress(30)
            
#             audio_path = save_upload_to_temp(uploaded)
            
#             st.info("🎤 Transcribing audio...")
#             progress_bar.progress(50)
            
#             lang = None if lang_hint == "auto" else lang_hint
#             transcript = transcribe_audio(client, audio_path, lang)
#             content_analysis = f"Audio Content Analysis:\n{transcript}"
            
#             st.success("✓ Audio transcribed")
            
#             with st.expander("View Transcript"):
#                 st.text_area("Transcription:", transcript, height=200)
            
#             selected_commands = []
#             if manual_command == "AUTO-DETECT":
#                 status_text.text("🤖 Detecting news type...")
#                 progress_bar.progress(60)
#                 detected_type = auto_detect_news_type(content_analysis, client)
#                 selected_commands = detected_type
#                 st.success(f"✓ Detected: {detected_type[0]}")
#             else:
#                 selected_commands = [manual_command]
            
#             selected_model = get_optimal_model("audio", selected_commands, file_size_mb)
            
#             status_text.text("📺 Creating Telugu script...")
#             progress_bar.progress(80)
            
#             with st.spinner("AI is writing Telugu news script..."):
#                 tv_scripts = generate_tv_news_script_multilingual(
#                     client=client,
#                     model=selected_model,
#                     source_type="audio",
#                     command_types=selected_commands,
#                     languages=languages,
#                     transcript=transcript,
#                     content_analysis=content_analysis,
#                     town=town or None,
#                     incident_time=incident_time or None
#                 )
            
#             progress_bar.progress(100)
#             status_text.text("✅ Complete!")
            
#             st.success("### 📺 Telugu Script Generated!")
#             display_tv_script_multilingual(tv_scripts, selected_commands, selected_model)
            
#             st.divider()
#             st.markdown("### 📥 Download Script")
            
#             script_paths = save_tv_script_output_multilingual(tv_scripts, "audio", selected_commands)
#             output_folder = os.path.dirname(list(script_paths.values())[0]) if script_paths else ""
            
#             if "te" in script_paths:
#                 with open(script_paths["te"], "rb") as f:
#                     st.download_button(
#                         "📥 Download Telugu Script",
#                         data=f,
#                         file_name=os.path.basename(script_paths["te"]),
#                         mime="text/plain",
#                         use_container_width=True
#                     )
            
#             log_to_csv(
#                 source_type="AUDIO",
#                 input_file_name=uploaded.name,
#                 input_file_size_mb=file_size_mb,
#                 languages=languages,
#                 news_format=selected_commands[0] if selected_commands else "AUTO-DETECTED",
#                 location=town,
#                 incident_time=incident_time,
#                 ai_model=selected_model,
#                 output_files=list(script_paths.values()),
#                 output_folder=output_folder,
#                 status="SUCCESS",
#                 notes=f"Lang hint: {lang_hint}"
#             )
            
#             st.success(f"**✅ Saved to:** `{output_folder}`")
            
#         except Exception as e:
#             st.error(f"❌ Error: {str(e)}")
#             import traceback
#             st.code(traceback.format_exc())

# if __name__ == "__main__":
#     main()