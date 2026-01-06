import os
from datetime import datetime
import streamlit as st

from shared import (
    save_upload_to_temp, extract_audio_from_video, transcribe_audio,
    deep_analyze_video, auto_detect_news_type, get_optimal_model,
    generate_tv_news_script_multilingual, log_to_csv,
    generate_audio_from_script, VOICE_PRESETS
)


def process_video(video_file, client, manual_command, lang_hint, town, incident_time,
                 output_base=None, file_prefix="v1",
                 generate_audio=False, sarvam_api_key=None, voice_settings=None):
    
    file_size_mb = video_file.size / (1024 * 1024)
    progress = st.progress(0)
    status = st.empty()
    
    try:
        status.text("🔄 Extracting audio...")
        progress.progress(20)
        
        video_path = save_upload_to_temp(video_file)
        wav_path = os.path.join("temp", f"audio_{int(datetime.now().timestamp())}.wav")
        os.makedirs("temp", exist_ok=True)
        
        has_audio = True
        try:
            extract_audio_from_video(video_path, wav_path)
        except RuntimeError as e:
            if "no audio stream" in str(e).lower():
                st.warning("⚠️ Video has no audio - will use only visual analysis")
                has_audio = False
                transcript = ""
            else:
                raise
        
        progress.progress(40)
        
        if has_audio:
            status.text("🎤 Transcribing...")
            lang = None if lang_hint == "auto" else lang_hint
            try:
                transcript = transcribe_audio(client, wav_path, lang)
                st.success("✓ Transcribed")
            except Exception as e:
                st.warning(f"⚠️ Transcription failed: {str(e)} - Using visual analysis only")
                transcript = ""
        else:
            transcript = ""
        
        progress.progress(60)
        
        status.text("📸 Analyzing video...")
        content_analysis = deep_analyze_video(client, video_path)
        st.success("✓ Analyzed")
        
        with st.expander("📋 Analysis"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_area("Visual:", content_analysis, height=150, key=f"visual_{file_prefix}")
            with col2:
                st.text_area("Audio:", transcript, height=150, key=f"audio_{file_prefix}")
        
        progress.progress(70)
        
        if manual_command == "AUTO-DETECT":
            status.text("🤖 Detecting news type...")
            combined = f"VISUAL:\n{content_analysis}\n\nAUDIO:\n{transcript}"
            selected_commands = auto_detect_news_type(combined, client)
            st.info(f"Detected: {selected_commands[0]}")
        else:
            selected_commands = [manual_command]
        
        progress.progress(80)
        
        status.text("📺 Creating Telugu script...")
        model = get_optimal_model("video", selected_commands, file_size_mb)
        
        scripts = generate_tv_news_script_multilingual(
            client=client, model=model,
            source_type="video",
            command_types=selected_commands,
            languages=["te"],
            transcript=transcript,
            content_analysis=content_analysis,
            town=town or None,
            incident_time=incident_time or None
        )
        
        progress.progress(90)
        
        status.text("💾 Saving files...")
        
        if output_base:
            # Save video to video folder
            video_folder = os.path.join(output_base, "video")
            os.makedirs(video_folder, exist_ok=True)
            
            video_ext = os.path.splitext(video_file.name)[1]
            video_output_filename = f"{file_prefix}{video_ext}"
            video_output_path = os.path.join(video_folder, video_output_filename)
            
            # Copy the video file
            with open(video_path, "rb") as src, open(video_output_path, "wb") as dst:
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
            script_paths = save_tv_script_output_multilingual(scripts, "video", selected_commands)
            text_output_path = script_paths["te"]
            video_output_path = None
        
        audio_output_path = None
        if generate_audio and sarvam_api_key:
            try:
                status.text("🎙️ Generating audio...")
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
                    
                    audio_filename = f"{file_prefix}.mp3"
                    audio_output_path = os.path.join(audio_folder, audio_filename)
                else:
                    audio_output_path = None
                
                audio_output_path = generate_audio_from_script(
                    script_text=scripts["te"],
                    sarvam_api_key=sarvam_api_key,
                    speaker=speaker,
                    pitch=pitch,
                    pace=pace,
                    loudness=loudness,
                    sample_rate=sample_rate,
                    output_path=audio_output_path
                )
                
                st.success(f"✅ Audio generated with {VOICE_PRESETS[speaker]['name']} voice!")
                
            except Exception as e:
                error_msg = str(e)
                if "Subscription not found" in error_msg or "403" in error_msg:
                    st.warning("⚠️ TTS generation failed: Invalid or expired Sarvam AI API key.")
                else:
                    st.warning(f"⚠️ Audio generation failed: {error_msg}")
                audio_output_path = None
        
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
        
        if video_output_path and os.path.exists(video_output_path):
            with col2:
                st.info(f"📹 Video saved: {os.path.basename(video_output_path)}")
        
        if audio_output_path and os.path.exists(audio_output_path):
            with col3:
                with open(audio_output_path, "rb") as f:
                    st.download_button(
                        "📥 Download Audio (MP3)",
                        data=f,
                        file_name=os.path.basename(audio_output_path),
                        mime="audio/mp3",
                        key=f"download_audio_{file_prefix}"
                    )
            
            st.markdown("### 🔊 Listen to Generated Audio")
            with open(audio_output_path, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
        
        output_files = [text_output_path]
        if video_output_path:
            output_files.append(video_output_path)
        if audio_output_path:
            output_files.append(audio_output_path)
        
        try:
            log_to_csv(
                source_type="VIDEO",
                input_file_name=video_file.name,
                input_file_size_mb=file_size_mb,
                languages=["te"],
                news_format=selected_commands[0],
                location=town,
                incident_time=incident_time,
                ai_model=model,
                output_files=output_files,
                audio_generated=audio_output_path is not None,
                status="SUCCESS",
                notes=f"Prefix: {file_prefix}, Lang: {lang_hint}"
            )
        except Exception as log_error:
            st.warning(f"Could not log to CSV: {log_error}")
        
        return {
            'status': 'SUCCESS',
            'output_file': text_output_path,
            'video_file': video_output_path,
            'audio_file': audio_output_path,
            'news_format': selected_commands[0],
            'model': model
        }
        
    except Exception as e:
        status.text("❌ Failed")
        st.error(f"Error: {str(e)}")
        
        try:
            log_to_csv(
                source_type="VIDEO",
                input_file_name=video_file.name,
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
#     ensure_dirs, file_to_data_url, save_upload_to_temp, make_client,
#     extract_audio_from_video, transcribe_audio,
#     deep_analyze_video, auto_detect_news_type,
#     generate_tv_news_script_multilingual,
#     save_tv_script_output_multilingual, display_tv_script_multilingual,
#     log_to_csv
# )

# load_dotenv()
# ensure_dirs()

# def main():
#     st.set_page_config(
#         page_title="AI TV News Script Generator - Video (Telugu)",
#         layout="wide",
#         page_icon="🎥"
#     )
    
#     st.title("🎥 AI-Powered TV News Script Generator - Video")
#     st.caption("Upload Videos → AI Analyzes Visuals & Audio → Generates Professional Telugu Broadcast Scripts")
    
#     with st.sidebar:
#         st.header("⚙️ Configuration")
        
#         st.subheader("🔐 OpenAI API Key")
#         env_key = os.getenv("OPENAI_API_KEY", "")
#         api_key = st.text_input("API Key", value=env_key, type="password")
        
#         st.info("""
#         **✨ Features for Videos:**
#         - Multi-frame visual analysis
#         - Audio transcription
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
        
#         st.warning("**Note:** Requires ffmpeg installed")
        
#         st.divider()
#         st.info("**📂 Output:** `C:\\Users\\GLOBAL T\\Desktop\\output\\`")
    
#     st.markdown("### 🎥 Upload News Video")
    
#     col1, col2 = st.columns([1, 1])
    
#     with col1:
#         uploaded = st.file_uploader(
#             "Upload Video",
#             type=["mp4", "mov", "avi", "mkv", "webm"]
#         )
        
#         if uploaded:
#             file_size = uploaded.size / (1024 * 1024)
#             st.success(f"✓ Video uploaded ({file_size:.1f} MB)")
#             st.video(uploaded)
    
#     with col2:
#         st.markdown("### 🚀 Generate Telugu Script")
#         st.info("**Output:** 🇮🇳 Telugu Script Only")
        
#         can_generate = api_key.strip() and uploaded
        
#         generate_btn = st.button(
#             "🎬 GENERATE TELUGU BROADCAST SCRIPT",
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
#             status_text.text("🔄 Processing video...")
#             progress_bar.progress(20)
            
#             video_path = save_upload_to_temp(uploaded)
            
#             st.info("🎥 Extracting audio...")
#             progress_bar.progress(30)
            
#             wav_path = os.path.join("temp", f"audio_{int(datetime.now().timestamp())}.wav")
#             extract_audio_from_video(video_path, wav_path)
            
#             progress_bar.progress(40)
            
#             lang = None if lang_hint == "auto" else lang_hint
#             transcript = transcribe_audio(client, wav_path, lang)
#             st.success("✓ Audio transcribed")
            
#             progress_bar.progress(50)
            
#             st.info("📸 Analyzing video frames...")
#             content_analysis = deep_analyze_video(client, video_path)
#             st.success("✓ Video analyzed")
            
#             with st.expander("View Analysis & Transcript"):
#                 st.text_area("Visual Analysis:", content_analysis, height=150)
#                 st.text_area("Transcript:", transcript, height=150)
            
#             selected_commands = []
#             if manual_command == "AUTO-DETECT":
#                 status_text.text("🤖 Detecting news type...")
#                 progress_bar.progress(60)
#                 combined = f"VISUAL:\n{content_analysis}\n\nAUDIO:\n{transcript}"
#                 detected_type = auto_detect_news_type(combined, client)
#                 selected_commands = detected_type
#                 st.success(f"✓ Detected: {detected_type[0]}")
#             else:
#                 selected_commands = [manual_command]
            
#             selected_model = get_optimal_model("video", selected_commands, file_size_mb)
            
#             status_text.text("📺 Creating Telugu script...")
#             progress_bar.progress(80)
            
#             with st.spinner("AI is writing Telugu news script..."):
#                 tv_scripts = generate_tv_news_script_multilingual(
#                     client=client,
#                     model=selected_model,
#                     source_type="video",
#                     command_types=selected_commands,
#                     languages=languages,
#                     video_path=video_path,
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
            
#             script_paths = save_tv_script_output_multilingual(tv_scripts, "video", selected_commands)
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
#                 source_type="VIDEO",
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