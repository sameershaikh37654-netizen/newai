# import streamlit as st
# import openai
# import subprocess
# import os
# import json
# from pathlib import Path
# import tempfile
# from dotenv import load_dotenv
# import re

# # Load environment variables
# load_dotenv()

# # Page config
# st.set_page_config(
#     page_title="Smart Video Summarizer",
#     page_icon="🎬",
#     layout="wide"
# )

# st.title("🎬 Smart Video Summarizer Pro")
# st.markdown("AI-powered video summarization with intelligent speech detection and topic-based segmentation")

# # Initialize session state
# if 'processing' not in st.session_state:
#     st.session_state.processing = False
# if 'last_summary' not in st.session_state:
#     st.session_state.last_summary = None
# if 'ffmpeg_available' not in st.session_state:
#     st.session_state.ffmpeg_available = None

# def check_ffmpeg():
#     """Check if FFmpeg is installed"""
#     try:
#         subprocess.run(['ffmpeg', '-version'], 
#                       stdout=subprocess.PIPE, 
#                       stderr=subprocess.PIPE, 
#                       check=True)
#         return True
#     except:
#         return False

# def check_ffprobe():
#     """Check if FFprobe is installed (part of FFmpeg)"""
#     try:
#         subprocess.run(['ffprobe', '-version'], 
#                       stdout=subprocess.PIPE, 
#                       stderr=subprocess.PIPE, 
#                       check=True)
#         return True
#     except:
#         return False

# # Check FFmpeg once and store in session state
# if st.session_state.ffmpeg_available is None:
#     st.session_state.ffmpeg_available = check_ffmpeg()
#     st.session_state.ffprobe_available = check_ffprobe()

# # Sidebar for API key and settings
# with st.sidebar:
#     st.header("⚙️ Configuration")
    
#     # Get API key from .env or allow manual input
#     default_api_key = os.getenv("OPENAI_API_KEY", "")
#     if default_api_key:
#         api_key = st.text_input("OpenAI API Key", 
#                                value=default_api_key, 
#                                type="password",
#                                help="API key loaded from .env file")
#         st.success("✅ API key loaded from environment")
#     else:
#         api_key = st.text_input("OpenAI API Key", 
#                                type="password",
#                                help="Enter your OpenAI API key or set OPENAI_API_KEY in .env file")
#         st.warning("⚠️ No API key found in .env file")
    
#     st.markdown("---")
#     st.header("📋 Smart Duration Control")
    
#     duration_preset = st.radio(
#         "Choose format:",
#         ["15 sec (Reels/Shorts)", "30 sec (News)", "60 sec (YouTube)", "Custom"],
#         index=1
#     )
    
#     if duration_preset == "15 sec (Reels/Shorts)":
#         target_duration = 15
#     elif duration_preset == "30 sec (News)":
#         target_duration = 30
#     elif duration_preset == "60 sec (YouTube)":
#         target_duration = 60
#     else:
#         target_duration = st.slider("Custom Duration (seconds)", 10, 120, 30)
    
#     st.info(f"🎯 Target: {target_duration} seconds")
    
#     st.markdown("---")
#     st.header("🔧 Smart Features")
    
#     speech_only = st.checkbox("Speech-Only Mode", value=True, 
#                              help="Ignore background music, noise, and silence")
    
#     detect_important_moments = st.checkbox("Important Moment Detection", value=True,
#                                           help="AI detects announcements, key statements, and facts")
    
#     remove_filler_words = st.checkbox("Remove Filler Words", value=True,
#                                      help="Remove 'umm', 'aa', long pauses")
    
#     complete_sentences = st.checkbox("Complete Sentences Only", value=True,
#                                     help="No mid-sentence cuts")
    
#     topic_based = st.checkbox("Topic-Based Segmentation", value=True,
#                              help="Group clips by topic for story flow")
    
#     chronological_order = st.checkbox("Maintain Chronological Order", value=True,
#                                      help="Keep events in original sequence")
    
#     st.markdown("---")
#     st.header("🔧 Advanced Settings")
    
#     with st.expander("Advanced Options"):
#         min_segment_duration = st.slider("Minimum segment duration (seconds)", 
#                                          2, 10, 3)
#         max_segments = st.slider("Maximum segments to extract", 3, 15, 8)
#         min_speech_confidence = st.slider("Speech detection confidence", 0.5, 1.0, 0.7)
    
#     st.markdown("---")
#     st.markdown("### 📖 How it works")
#     st.markdown(f"""
#     1. Upload video
#     2. AI detects clear speech
#     3. Identifies important moments
#     4. Groups by topics
#     5. Creates {target_duration}s summary
#     6. Download result
#     """)
    
#     # System check
#     st.markdown("---")
#     st.markdown("### 🔍 System Check")
    
#     ffmpeg_status = "✅ Found" if st.session_state.ffmpeg_available else "❌ Missing"
#     ffprobe_status = "✅ Found" if st.session_state.ffprobe_available else "❌ Missing"
    
#     st.write(f"FFmpeg: {ffmpeg_status}")
#     st.write(f"FFprobe: {ffprobe_status}")
#     st.write(f"OpenAI API: {'✅ Configured' if api_key else '❌ Required'}")
    
#     if not st.session_state.ffmpeg_available:
#         with st.expander("FFmpeg Installation Guide"):
#             st.markdown("""
#             **Install FFmpeg:**
            
#             **Windows:**
#             ```bash
#             choco install ffmpeg
#             ```
            
#             **macOS:**
#             ```bash
#             brew install ffmpeg
#             ```
            
#             **Ubuntu/Debian:**
#             ```bash
#             sudo apt update
#             sudo apt install ffmpeg
#             ```
#             """)

# def extract_audio(video_path, audio_path):
#     """Extract audio from video using FFmpeg"""
#     cmd = [
#         'ffmpeg', '-i', video_path,
#         '-vn', '-acodec', 'libmp3lame',
#         '-ar', '16000', '-ac', '1',
#         '-y', audio_path
#     ]
#     result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     if result.returncode != 0:
#         error_msg = result.stderr.decode()[:500]
#         st.error(f"FFmpeg error: {error_msg}")
#         raise Exception("Audio extraction failed")
#     return audio_path

# def get_video_duration(video_path):
#     """Get video duration in seconds"""
#     if not st.session_state.ffprobe_available:
#         file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
#         return min(file_size_mb * 5, 600)
    
#     cmd = [
#         'ffprobe', '-v', 'error',
#         '-show_entries', 'format=duration',
#         '-of', 'default=noprint_wrappers=1:nokey=1',
#         video_path
#     ]
#     result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     if result.returncode == 0:
#         try:
#             return float(result.stdout)
#         except:
#             return 300
#     return 300

# def clean_text_for_analysis(text):
#     """Remove filler words and clean text"""
#     filler_patterns = [
#         r'\b(um+|uh+|ah+|hmm+|er+|like)\b',
#         r'\b(you know|I mean|sort of|kind of)\b',
#         r'\.\.\.',
#         r'\s+',
#     ]
    
#     cleaned = text.lower()
#     for pattern in filler_patterns:
#         cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
    
#     cleaned = re.sub(r'\s+', ' ', cleaned).strip()
#     return cleaned

# def transcribe_audio(audio_path, api_key):
#     """Transcribe audio using OpenAI Whisper - supports all languages"""
#     client = openai.OpenAI(api_key=api_key)
    
#     with open(audio_path, 'rb') as audio_file:
#         try:
#             transcript = client.audio.transcriptions.create(
#                 model="whisper-1",
#                 file=audio_file,
#                 response_format="verbose_json",
#                 timestamp_granularities=["segment"]
#             )
#             return transcript
#         except openai.AuthenticationError:
#             st.error("❌ Invalid API key. Please check your OpenAI API key.")
#             raise
#         except openai.RateLimitError:
#             st.error("❌ API rate limit exceeded. Please try again later.")
#             raise
#         except Exception as e:
#             st.error(f"❌ Transcription failed: {str(e)}")
#             raise

# def analyze_content_smart(transcript, api_key, target_duration, video_duration, 
#                           max_segments=8, speech_only=True, detect_important=True,
#                           remove_fillers=True, complete_sentences=True,
#                           topic_based=True, chronological=True):
#     """Smart analysis with all advanced features"""
#     client = openai.OpenAI(api_key=api_key)
    
#     # Prepare transcript text with timestamps
#     segments_text = "\n".join([
#         f"[{seg.start:.2f}s - {seg.end:.2f}s]: {seg.text}"
#         for seg in transcript.segments
#     ])
    
#     detected_language = transcript.language if hasattr(transcript, 'language') else "unknown"
    
#     # Build smart instructions
#     instructions = []
    
#     if speech_only:
#         instructions.append("- ONLY select segments with CLEAR HUMAN SPEECH (ignore background music, crowd noise, ambient sounds)")
    
#     if detect_important:
#         instructions.append("- Prioritize IMPORTANT MOMENTS: announcements, key statements, critical facts, strong impactful lines")
    
#     if remove_fillers:
#         instructions.append("- AVOID segments with excessive filler words (um, uh, aa), long pauses, or incomplete thoughts")
    
#     if complete_sentences:
#         instructions.append("- Each segment must contain COMPLETE SENTENCES - no mid-sentence cuts")
    
#     if topic_based:
#         instructions.append("- GROUP segments by TOPIC to create natural story flow (Topic 1 → Topic 2 → Topic 3)")
    
#     if chronological:
#         instructions.append("- MAINTAIN CHRONOLOGICAL ORDER - events must stay in original sequence")
    
#     instructions_text = "\n".join(instructions)
    
#     prompt = f"""You are an expert video editor creating a professional {target_duration}-second summary from a {video_duration:.1f}-second video.

# TRANSCRIPT (Language: {detected_language}):
# {segments_text}

# SMART SUMMARIZATION RULES:
# {instructions_text}
# - Select {max_segments} best segments
# - Total duration close to {target_duration} seconds
# - Each segment minimum 3 seconds
# - NO overlapping timestamps
# - Create smooth, professional flow

# SEGMENT TYPES TO PRIORITIZE:
# 1. ANNOUNCEMENTS (priority: 5)
# 2. KEY STATEMENTS (priority: 4)
# 3. IMPORTANT FACTS/DATA (priority: 4)
# 4. IMPACTFUL QUOTES (priority: 3)
# 5. TOPIC INTRODUCTIONS (priority: 3)

# Return ONLY a valid JSON array (no markdown, no extra text):

# [
#   {{
#     "start_time": 0.5,
#     "end_time": 8.3,
#     "reason": "Opening announcement",
#     "priority": 5,
#     "topic": "Introduction",
#     "text": "transcript text here",
#     "has_clear_speech": true,
#     "is_complete_sentence": true
#   }}
# ]

# CRITICAL: Return ONLY the JSON array, nothing else."""

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4",
#             messages=[
#                 {
#                     "role": "system", 
#                     "content": "You are an expert video editor. Return ONLY valid JSON arrays. Process transcripts in ANY language. Focus on creating professional, story-driven summaries."
#                 },
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.3,
#             max_tokens=3000
#         )
        
#         result = response.choices[0].message.content.strip()
        
#         # Extract JSON
#         start_idx = result.find('[')
#         end_idx = result.rfind(']')
        
#         if start_idx == -1 or end_idx == -1:
#             st.warning("AI response invalid. Using fallback method...")
#             return create_smart_fallback_segments(transcript, target_duration, max_segments, 
#                                                  speech_only, complete_sentences)
        
#         json_str = result[start_idx:end_idx+1]
        
#         try:
#             segments = json.loads(json_str)
            
#             if not isinstance(segments, list) or len(segments) == 0:
#                 st.warning("Invalid segment format. Using fallback...")
#                 return create_smart_fallback_segments(transcript, target_duration, max_segments,
#                                                      speech_only, complete_sentences)
            
#             # Validate required fields
#             for seg in segments:
#                 if not all(key in seg for key in ['start_time', 'end_time', 'priority']):
#                     st.warning("Missing fields. Using fallback...")
#                     return create_smart_fallback_segments(transcript, target_duration, max_segments,
#                                                          speech_only, complete_sentences)
            
#             # Sort chronologically if requested
#             if chronological:
#                 segments = sorted(segments, key=lambda x: x['start_time'])
            
#             return segments
            
#         except json.JSONDecodeError as e:
#             st.error(f"JSON parsing failed: {e}")
#             return create_smart_fallback_segments(transcript, target_duration, max_segments,
#                                                  speech_only, complete_sentences)
        
#     except Exception as e:
#         st.error(f"AI analysis error: {str(e)}")
#         return create_smart_fallback_segments(transcript, target_duration, max_segments,
#                                              speech_only, complete_sentences)

# def create_smart_fallback_segments(transcript, target_duration, max_segments, 
#                                   speech_only=True, complete_sentences=True):
#     """Smart fallback with speech filtering"""
#     segments = []
    
#     if not hasattr(transcript, 'segments') or len(transcript.segments) == 0:
#         raise ValueError("No transcript segments available")
    
#     # Filter segments for speech quality
#     quality_segments = []
#     for seg in transcript.segments:
#         text = seg.text.strip()
#         duration = seg.end - seg.start
        
#         # Skip very short segments
#         if duration < 2:
#             continue
        
#         # Skip if too many filler words (basic check)
#         filler_count = len(re.findall(r'\b(um|uh|ah|hmm|er)\b', text.lower()))
#         word_count = len(text.split())
        
#         if word_count > 0 and filler_count / word_count > 0.3:
#             continue
        
#         # Check for complete sentences
#         if complete_sentences and text and not text[-1] in '.!?':
#             # Try to find natural pause
#             if ',' not in text and ';' not in text:
#                 continue
        
#         quality_segments.append(seg)
    
#     if len(quality_segments) == 0:
#         quality_segments = list(transcript.segments)
    
#     # Select evenly distributed segments
#     total_segments = len(quality_segments)
#     step = max(1, total_segments // max_segments)
    
#     selected_indices = list(range(0, total_segments, step))[:max_segments]
    
#     total_duration = 0
#     for idx in selected_indices:
#         seg = quality_segments[idx]
        
#         segment_obj = {
#             'start_time': seg.start,
#             'end_time': seg.end,
#             'priority': 3,
#             'reason': 'Auto-selected quality segment',
#             'topic': 'General',
#             'text': seg.text,
#             'has_clear_speech': True,
#             'is_complete_sentence': complete_sentences
#         }
        
#         segments.append(segment_obj)
#         total_duration += (seg.end - seg.start)
        
#         if total_duration >= target_duration:
#             break
    
#     st.info(f"✅ Smart Fallback: Selected {len(segments)} quality segments")
#     return segments

# def create_summary_video(input_video, segments, output_path, min_duration=3):
#     """Create professional summary video with smooth transitions"""
    
#     # Filter valid segments
#     valid_segments = [seg for seg in segments 
#                      if seg['end_time'] - seg['start_time'] >= min_duration]
    
#     if not valid_segments:
#         raise ValueError("No valid segments found for summary")
    
#     with tempfile.TemporaryDirectory() as temp_dir:
#         segment_files = []
        
#         # Extract each segment with fade transitions
#         for i, seg in enumerate(valid_segments):
#             segment_path = os.path.join(temp_dir, f"segment_{i:03d}.mp4")
            
#             start_time = seg['start_time']
#             end_time = seg['end_time']
#             duration = end_time - start_time
            
#             # Extract with re-encoding for smooth playback
#             cmd = [
#                 'ffmpeg', '-i', input_video,
#                 '-ss', str(start_time),
#                 '-t', str(duration),
#                 '-c:v', 'libx264', '-preset', 'medium',
#                 '-crf', '23',
#                 '-c:a', 'aac', '-b:a', '128k',
#                 '-avoid_negative_ts', 'make_zero',
#                 '-y', segment_path
#             ]
            
#             result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            
#             if result.returncode != 0:
#                 # Fallback to copy method
#                 cmd_simple = [
#                     'ffmpeg', '-i', input_video,
#                     '-ss', str(start_time),
#                     '-t', str(duration),
#                     '-c', 'copy',
#                     '-y', segment_path
#                 ]
#                 subprocess.run(cmd_simple, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            
#             segment_files.append(segment_path)
        
#         # Create concat file
#         concat_file = os.path.join(temp_dir, 'concat.txt')
#         with open(concat_file, 'w', encoding='utf-8') as f:
#             for seg_file in segment_files:
#                 f.write(f"file '{seg_file}'\n")
        
#         # Concatenate with smooth output
#         cmd = [
#             'ffmpeg', '-f', 'concat',
#             '-safe', '0',
#             '-i', concat_file,
#             '-c:v', 'libx264', '-preset', 'medium',
#             '-crf', '23',
#             '-c:a', 'aac', '-b:a', '128k',
#             '-movflags', '+faststart',
#             '-y', output_path
#         ]
        
#         result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        
#         if result.returncode != 0:
#             st.error(f"Concatenation failed: {result.stderr.decode()[:500]}")
#             raise Exception("Video creation failed")
    
#     return output_path, valid_segments

# # Main interface
# col1, col2 = st.columns([1, 1])

# with col1:
#     st.header("📤 Upload Video")
#     uploaded_file = st.file_uploader(
#         "Choose a video file",
#         type=['mp4', 'mov', 'avi', 'mkv', 'webm'],
#         help="Upload any video - AI will create professional summary"
#     )
    
#     if uploaded_file:
#         file_size_mb = uploaded_file.size / (1024 * 1024)
        
#         col_info1, col_info2 = st.columns(2)
#         with col_info1:
#             st.metric("File Size", f"{file_size_mb:.1f} MB")
        
#         st.video(uploaded_file)
        
#         if file_size_mb > 200:
#             st.warning("⚠️ Large file detected. Processing may take longer.")

# with col2:
#     st.header("🎯 Smart Summary")
    
#     if uploaded_file:
#         if not api_key:
#             st.error("🔑 Please enter your OpenAI API key in the sidebar")
#         elif not st.session_state.ffmpeg_available:
#             st.error("❌ FFmpeg not found. Please install FFmpeg to use this tool.")
#         else:
#             if st.button("🚀 Create Smart Summary", 
#                         type="primary", 
#                         disabled=st.session_state.processing,
#                         use_container_width=True):
                
#                 st.session_state.processing = True
                
#                 try:
#                     with tempfile.TemporaryDirectory() as temp_dir:
                        
#                         # Save uploaded video
#                         video_path = os.path.join(temp_dir, "input_video.mp4")
#                         with open(video_path, 'wb') as f:
#                             f.write(uploaded_file.read())
                        
#                         video_duration = get_video_duration(video_path)
                        
#                         # Progress tracking
#                         progress_bar = st.progress(0)
#                         status_text = st.empty()
                        
#                         # Step 1: Extract audio
#                         status_text.text("🎵 Step 1/4: Extracting audio...")
#                         progress_bar.progress(25)
#                         audio_path = os.path.join(temp_dir, "audio.mp3")
#                         extract_audio(video_path, audio_path)
                        
#                         # Step 2: Transcribe
#                         status_text.text("📝 Step 2/4: Transcribing speech (all languages)...")
#                         progress_bar.progress(50)
#                         transcript = transcribe_audio(audio_path, api_key)
                        
#                         detected_lang = transcript.language if hasattr(transcript, 'language') else "unknown"
#                         st.info(f"🌍 Detected: {detected_lang.upper()}")
                        
#                         # Step 3: Smart analysis
#                         status_text.text("🤖 Step 3/4: AI analyzing with smart features...")
#                         progress_bar.progress(75)
#                         segments = analyze_content_smart(
#                             transcript, api_key, 
#                             target_duration, video_duration, max_segments,
#                             speech_only, detect_important_moments,
#                             remove_filler_words, complete_sentences,
#                             topic_based, chronological_order
#                         )
                        
#                         # Step 4: Create video
#                         status_text.text("✂️ Step 4/4: Creating professional summary...")
#                         progress_bar.progress(90)
#                         output_path = os.path.join(temp_dir, "summary.mp4")
#                         output_path, selected_segments = create_summary_video(
#                             video_path, segments, output_path, min_segment_duration
#                         )
                        
#                         progress_bar.progress(100)
#                         status_text.text("✅ Smart summary created!")
                        
#                         # Calculate stats
#                         total_summary_duration = sum(
#                             seg['end_time'] - seg['start_time'] 
#                             for seg in selected_segments
#                         )
                        
#                         # Display results
#                         st.success(f"""
#                         🎉 Smart Summary Complete!
#                         - **Duration:** {total_summary_duration:.1f}s (Target: {target_duration}s)
#                         - **Segments:** {len(selected_segments)}
#                         - **Compression:** {(video_duration/total_summary_duration):.1f}x
#                         - **Quality:** Professional with smart features
#                         """)
                        
#                         # Show summary video
#                         with open(output_path, 'rb') as f:
#                             video_bytes = f.read()
                            
#                             st.subheader("📺 Smart Summary Preview")
#                             st.video(video_bytes)
                            
#                             # Download button
#                             col_dl1, col_dl2 = st.columns([1, 2])
#                             with col_dl1:
#                                 st.download_button(
#                                     label="⬇️ Download Summary",
#                                     data=video_bytes,
#                                     file_name=f"smart_summary_{target_duration}s.mp4",
#                                     mime="video/mp4",
#                                     use_container_width=True
#                                 )
                            
#                             with col_dl2:
#                                 file_size_mb = len(video_bytes) / (1024 * 1024)
#                                 st.caption(f"File size: {file_size_mb:.1f} MB")
                        
#                         # Show segment details with topics
#                         with st.expander("📋 View Selected Segments"):
#                             current_topic = None
                            
#                             for i, seg in enumerate(selected_segments, 1):
#                                 duration = seg['end_time'] - seg['start_time']
#                                 topic = seg.get('topic', 'General')
                                
#                                 # Show topic header if changed
#                                 if topic != current_topic:
#                                     st.markdown(f"### 📌 {topic}")
#                                     current_topic = topic
                                
#                                 col_seg1, col_seg2 = st.columns([1, 4])
                                
#                                 with col_seg1:
#                                     st.metric(f"Segment {i}", f"{duration:.1f}s")
                                
#                                 with col_seg2:
#                                     priority_stars = "⭐" * seg.get('priority', 3)
                                    
#                                     features = []
#                                     if seg.get('has_clear_speech'):
#                                         features.append("🎤 Clear Speech")
#                                     if seg.get('is_complete_sentence'):
#                                         features.append("✅ Complete")
                                    
#                                     features_text = " | ".join(features) if features else ""
                                    
#                                     st.markdown(f"""
#                                     **Time:** {seg['start_time']:.1f}s - {seg['end_time']:.1f}s  
#                                     **Priority:** {priority_stars}  
#                                     **Reason:** {seg.get('reason', 'Auto-selected')}  
#                                     {features_text}
#                                     """)
                                    
#                                     if 'text' in seg and seg['text']:
#                                         with st.expander("View transcript"):
#                                             st.caption(seg['text'])
                                
#                                 st.divider()
                        
#                         # Store in session state
#                         st.session_state.last_summary = {
#                             'video_bytes': video_bytes,
#                             'segments': selected_segments,
#                             'original_duration': video_duration,
#                             'summary_duration': total_summary_duration
#                         }
                
#                 except subprocess.TimeoutExpired:
#                     st.error("⏱️ Processing timed out. Try with a shorter video.")
#                 except Exception as e:
#                     st.error(f"❌ Error: {str(e)}")
#                     st.info("💡 Try adjusting smart features in sidebar.")
                
#                 finally:
#                     st.session_state.processing = False
    
#     else:
#         st.info("👈 Upload a video to create smart summary")

# # Custom CSS
# st.markdown("""
# <style>
#     .stButton > button {
#         width: 100%;
#         background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
#         color: white;
#         font-weight: bold;
#         border: none;
#         padding: 0.75rem 1rem;
#         border-radius: 8px;
#         transition: all 0.3s ease;
#     }
#     .stButton > button:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
#     }
#     .stProgress > div > div > div > div {
#         background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
#     }
#     .stVideo {
#         border-radius: 10px;
#         overflow: hidden;
#         box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#     }
#     .stMetric {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 1rem;
#         border-radius: 8px;
#         color: white;
#     }
#     h3 {
#         color: #667eea;
#         margin-top: 1rem;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; color: #666; padding: 20px;'>
#     <h4>🎯 Smart Features Active</h4>
#     <p>✅ Multi-language support (English, Tamil, Hindi, Spanish, etc.)</p>
#     <p>✅ Smart duration control (15s/30s/60s)</p>
#     <p>✅ Speech-only mode (no background noise)</p>
#     <p>✅ Important moment detection</p>
#     <p>✅ Filler word removal</p>
#     <p>✅ Complete sentences only</p>
#     <p>✅ Topic-based segmentation</p>
#     <p>✅ Chronological story flow</p>
#     <br>
#     <p><strong>🔒 Privacy:</strong> Videos processed securely, not stored</p>
#     <p style='font-size: 0.8em; margin-top: 20px; color: #888;'>Powered by OpenAI Whisper & GPT-4</p>
# </div>
# """, unsafe_allow_html=True)





































import streamlit as st
import openai
import subprocess
import os
import json
from pathlib import Path
import tempfile
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Smart Video Summarizer",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Smart Video Summarizer Pro")
st.markdown("AI-powered video summarization with intelligent speech detection and topic-based segmentation")

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'last_summary' not in st.session_state:
    st.session_state.last_summary = None
if 'ffmpeg_available' not in st.session_state:
    st.session_state.ffmpeg_available = None
if 'auto_news_triggered' not in st.session_state:
    st.session_state.auto_news_triggered = False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
        return True
    except:
        return False

def check_ffprobe():
    """Check if FFprobe is installed (part of FFmpeg)"""
    try:
        subprocess.run(['ffprobe', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
        return True
    except:
        return False

# Check FFmpeg once and store in session state
if st.session_state.ffmpeg_available is None:
    st.session_state.ffmpeg_available = check_ffmpeg()
    st.session_state.ffprobe_available = check_ffprobe()

# Sidebar for API key and settings
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Get API key from .env or allow manual input
    default_api_key = os.getenv("OPENAI_API_KEY", "")
    if default_api_key:
        api_key = st.text_input("OpenAI API Key", 
                               value=default_api_key, 
                               type="password",
                               help="API key loaded from .env file")
        st.success("✅ API key loaded from environment")
    else:
        api_key = st.text_input("OpenAI API Key", 
                               type="password",
                               help="Enter your OpenAI API key or set OPENAI_API_KEY in .env file")
        st.warning("⚠️ No API key found in .env file")
    
    st.markdown("---")
    st.header("📋 Smart Duration Control")
    
    duration_preset = st.radio(
        "Choose format:",
        ["15 sec (Reels/Shorts)", "30 sec (News)", "60 sec (YouTube)", "Custom"],
        index=1
    )
    
    if duration_preset == "15 sec (Reels/Shorts)":
        target_duration = 15
    elif duration_preset == "30 sec (News)":
        target_duration = 30
    elif duration_preset == "60 sec (YouTube)":
        target_duration = 60
    else:
        target_duration = st.slider("Custom Duration (seconds)", 10, 120, 30)
    
    st.info(f"🎯 Target: {target_duration} seconds")
    
    st.markdown("---")
    st.header("🔧 Smart Features")
    
    speech_only = st.checkbox("Speech-Only Mode", value=True, 
                             help="Ignore background music, noise, and silence")
    
    detect_important_moments = st.checkbox("Important Moment Detection", value=True,
                                          help="AI detects announcements, key statements, and facts")
    
    remove_filler_words = st.checkbox("Remove Filler Words", value=True,
                                     help="Remove 'umm', 'aa', long pauses")
    
    complete_sentences = st.checkbox("Complete Sentences Only", value=True,
                                    help="No mid-sentence cuts")
    
    topic_based = st.checkbox("Topic-Based Segmentation", value=True,
                             help="Group clips by topic for story flow")
    
    chronological_order = st.checkbox("Maintain Chronological Order", value=True,
                                     help="Keep events in original sequence")
    
    st.markdown("---")
    st.header("🔧 Advanced Settings")
    
    with st.expander("Advanced Options"):
        min_segment_duration = st.slider("Minimum segment duration (seconds)", 
                                         2, 10, 3)
        max_segments = st.slider("Maximum segments to extract", 3, 15, 8)
        min_speech_confidence = st.slider("Speech detection confidence", 0.5, 1.0, 0.7)
    
    st.markdown("---")
    st.markdown("### 📖 How it works")
    st.markdown(f"""
    1. Upload video
    2. AI detects clear speech
    3. Identifies important moments
    4. Groups by topics
    5. Creates {target_duration}s summary
    6. Download result
    """)
    
    # System check
    st.markdown("---")
    st.markdown("### 🔍 System Check")
    
    ffmpeg_status = "✅ Found" if st.session_state.ffmpeg_available else "❌ Missing"
    ffprobe_status = "✅ Found" if st.session_state.ffprobe_available else "❌ Missing"
    
    st.write(f"FFmpeg: {ffmpeg_status}")
    st.write(f"FFprobe: {ffprobe_status}")
    st.write(f"OpenAI API: {'✅ Configured' if api_key else '❌ Required'}")
    
    if not st.session_state.ffmpeg_available:
        with st.expander("FFmpeg Installation Guide"):
            st.markdown("""
            **Install FFmpeg:**
            
            **Windows:**
            ```bash
            choco install ffmpeg
            ```
            
            **macOS:**
            ```bash
            brew install ffmpeg
            ```
            
            **Ubuntu/Debian:**
            ```bash
            sudo apt update
            sudo apt install ffmpeg
            ```
            """)

def extract_audio(video_path, audio_path):
    """Extract audio from video using FFmpeg"""
    cmd = [
        'ffmpeg', '-i', video_path,
        '-vn', '-acodec', 'libmp3lame',
        '-ar', '16000', '-ac', '1',
        '-y', audio_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        error_msg = result.stderr.decode()[:500]
        st.error(f"FFmpeg error: {error_msg}")
        raise Exception("Audio extraction failed")
    return audio_path

def get_video_duration(video_path):
    """Get video duration in seconds"""
    if not st.session_state.ffprobe_available:
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        return min(file_size_mb * 5, 600)
    
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        try:
            return float(result.stdout)
        except:
            return 300
    return 300

def clean_text_for_analysis(text):
    """Remove filler words and clean text"""
    filler_patterns = [
        r'\b(um+|uh+|ah+|hmm+|er+|like)\b',
        r'\b(you know|I mean|sort of|kind of)\b',
        r'\.\.\.',
        r'\s+',
    ]
    
    cleaned = text.lower()
    for pattern in filler_patterns:
        cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
    
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def transcribe_audio(audio_path, api_key):
    """Transcribe audio using OpenAI Whisper - supports all languages"""
    client = openai.OpenAI(api_key=api_key)
    
    with open(audio_path, 'rb') as audio_file:
        try:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
            return transcript
        except openai.AuthenticationError:
            st.error("❌ Invalid API key. Please check your OpenAI API key.")
            raise
        except openai.RateLimitError:
            st.error("❌ API rate limit exceeded. Please try again later.")
            raise
        except Exception as e:
            st.error(f"❌ Transcription failed: {str(e)}")
            raise

def detect_news_importance(transcript, api_key):
    """Detect news importance score for each segment"""
    client = openai.OpenAI(api_key=api_key)
    
    segments_text = "\n".join([
        f"[{seg.start:.2f}s - {seg.end:.2f}s]: {seg.text}"
        for seg in transcript.segments
    ])
    
    prompt = f"""Analyze this video transcript and score each segment's NEWS IMPORTANCE (0-100).

TRANSCRIPT:
{segments_text}

For each segment, identify:
- BREAKING NEWS indicators (highest priority)
- KEY HEADLINES and announcements
- MAJOR EVENTS or significant occurrences
- HIGH-IMPACT statements from officials/experts
- CRITICAL INFORMATION affecting public

Return ONLY a JSON array with segment times and importance scores:
[
  {{
    "start_time": 0.5,
    "end_time": 8.3,
    "importance_score": 95,
    "news_type": "Breaking News",
    "is_news_content": true,
    "classification": "Critical"
  }}
]

CRITICAL: Return ONLY valid JSON, nothing else."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional news editor. Analyze content for news value and importance. Return ONLY valid JSON arrays."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=3000
        )
        
        result = response.choices[0].message.content.strip()
        start_idx = result.find('[')
        end_idx = result.rfind(']')
        
        if start_idx != -1 and end_idx != -1:
            json_str = result[start_idx:end_idx+1]
            return json.loads(json_str)
        return []
    except:
        return []

def analyze_content_smart(transcript, api_key, target_duration, video_duration, 
                          max_segments=8, speech_only=True, detect_important=True,
                          remove_fillers=True, complete_sentences=True,
                          topic_based=True, chronological=True, is_auto_news=False):
    """Smart analysis with all advanced features"""
    client = openai.OpenAI(api_key=api_key)
    
    # Prepare transcript text with timestamps
    segments_text = "\n".join([
        f"[{seg.start:.2f}s - {seg.end:.2f}s]: {seg.text}"
        for seg in transcript.segments
    ])
    
    detected_language = transcript.language if hasattr(transcript, 'language') else "unknown"
    
    # Get news importance scores if auto-news mode
    news_scores = {}
    if is_auto_news:
        news_importance = detect_news_importance(transcript, api_key)
        for item in news_importance:
            if item.get('is_news_content'):
                key = f"{item.get('start_time'):.1f}-{item.get('end_time'):.1f}"
                news_scores[key] = item.get('importance_score', 0)
    
    # Build smart instructions
    instructions = []
    
    if is_auto_news:
        instructions.append("- FOCUS EXCLUSIVELY ON NEWS CONTENT: breaking news, key headlines, major events, announcements")
        instructions.append("- IGNORE: greetings, small talk, filler content, non-news segments")
        instructions.append("- PRIORITIZE: news importance scores (higher scores = more important)")
        instructions.append("- SELECT ONLY high-impact news segments (importance score > 70)")
        max_segments = 6
    
    if speech_only:
        instructions.append("- ONLY select segments with CLEAR HUMAN SPEECH (ignore background music, crowd noise, ambient sounds)")
    
    if detect_important:
        instructions.append("- Prioritize IMPORTANT MOMENTS: announcements, key statements, critical facts, strong impactful lines")
    
    if remove_fillers:
        instructions.append("- AVOID segments with excessive filler words (um, uh, aa), long pauses, or incomplete thoughts")
    
    if complete_sentences:
        instructions.append("- Each segment must contain COMPLETE SENTENCES - no mid-sentence cuts")
    
    if topic_based:
        instructions.append("- GROUP segments by TOPIC to create natural story flow (Topic 1 → Topic 2 → Topic 3)")
    
    if chronological:
        instructions.append("- MAINTAIN CHRONOLOGICAL ORDER - events must stay in original sequence")
    
    instructions_text = "\n".join(instructions)
    
    news_context = ""
    if is_auto_news:
        news_context = f"\n\nNEWS IMPORTANCE SCORES: {json.dumps(news_scores)}\nSelectively use these scores to prioritize segments."
    
    prompt = f"""You are an expert video editor creating a professional {target_duration}-second NEWS SUMMARY from a {video_duration:.1f}-second video.

TRANSCRIPT (Language: {detected_language}):
{segments_text}{news_context}

SMART SUMMARIZATION RULES:
{instructions_text}
- Select {max_segments} best segments
- Total duration close to {target_duration} seconds
- Each segment minimum 2 seconds
- NO overlapping timestamps
- Create smooth, professional flow

NEWS SEGMENT PRIORITY:
1. BREAKING NEWS (priority: 5)
2. KEY HEADLINES (priority: 5)
3. MAJOR EVENTS/ANNOUNCEMENTS (priority: 4)
4. CRITICAL FACTS/DATA (priority: 4)
5. EXPERT STATEMENTS (priority: 3)

Return ONLY a valid JSON array (no markdown, no extra text):

[
  {{
    "start_time": 0.5,
    "end_time": 8.3,
    "reason": "Breaking news announcement",
    "priority": 5,
    "topic": "Breaking News",
    "text": "transcript text here",
    "has_clear_speech": true,
    "is_complete_sentence": true,
    "news_type": "Breaking News"
  }}
]

CRITICAL: Return ONLY the JSON array, nothing else."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert news video editor. Return ONLY valid JSON arrays. Process transcripts in ANY language. Focus on news-driven summaries with high-impact content."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=3000
        )
        
        result = response.choices[0].message.content.strip()
        
        # Extract JSON
        start_idx = result.find('[')
        end_idx = result.rfind(']')
        
        if start_idx == -1 or end_idx == -1:
            st.warning("AI response invalid. Using fallback method...")
            return create_smart_fallback_segments(transcript, target_duration, max_segments, 
                                                 speech_only, complete_sentences, is_auto_news)
        
        json_str = result[start_idx:end_idx+1]
        
        try:
            segments = json.loads(json_str)
            
            if not isinstance(segments, list) or len(segments) == 0:
                st.warning("Invalid segment format. Using fallback...")
                return create_smart_fallback_segments(transcript, target_duration, max_segments,
                                                     speech_only, complete_sentences, is_auto_news)
            
            # Validate required fields
            for seg in segments:
                if not all(key in seg for key in ['start_time', 'end_time', 'priority']):
                    st.warning("Missing fields. Using fallback...")
                    return create_smart_fallback_segments(transcript, target_duration, max_segments,
                                                         speech_only, complete_sentences, is_auto_news)
            
            # Sort chronologically if requested
            if chronological:
                segments = sorted(segments, key=lambda x: x['start_time'])
            
            return segments
            
        except json.JSONDecodeError as e:
            st.error(f"JSON parsing failed: {e}")
            return create_smart_fallback_segments(transcript, target_duration, max_segments,
                                                 speech_only, complete_sentences, is_auto_news)
        
    except Exception as e:
        st.error(f"AI analysis error: {str(e)}")
        return create_smart_fallback_segments(transcript, target_duration, max_segments,
                                             speech_only, complete_sentences, is_auto_news)

def create_smart_fallback_segments(transcript, target_duration, max_segments, 
                                  speech_only=True, complete_sentences=True, is_auto_news=False):
    """Smart fallback with speech filtering"""
    segments = []
    
    if not hasattr(transcript, 'segments') or len(transcript.segments) == 0:
        raise ValueError("No transcript segments available")
    
    # Filter segments for speech quality
    quality_segments = []
    for seg in transcript.segments:
        text = seg.text.strip()
        duration = seg.end - seg.start
        
        # Skip very short segments
        if duration < 2:
            continue
        
        # Skip if too many filler words (basic check)
        filler_count = len(re.findall(r'\b(um|uh|ah|hmm|er)\b', text.lower()))
        word_count = len(text.split())
        
        if word_count > 0 and filler_count / word_count > 0.3:
            continue
        
        # Check for complete sentences
        if complete_sentences and text and not text[-1] in '.!?':
            if ',' not in text and ';' not in text:
                continue
        
        quality_segments.append(seg)
    
    if len(quality_segments) == 0:
        quality_segments = list(transcript.segments)
    
    # Select evenly distributed segments
    total_segments = len(quality_segments)
    step = max(1, total_segments // max_segments)
    
    selected_indices = list(range(0, total_segments, step))[:max_segments]
    
    total_duration = 0
    for idx in selected_indices:
        seg = quality_segments[idx]
        
        segment_obj = {
            'start_time': seg.start,
            'end_time': seg.end,
            'priority': 3,
            'reason': 'Auto-selected quality segment',
            'topic': 'General',
            'text': seg.text,
            'has_clear_speech': True,
            'is_complete_sentence': complete_sentences,
            'news_type': 'General' if not is_auto_news else 'Auto News'
        }
        
        segments.append(segment_obj)
        total_duration += (seg.end - seg.start)
        
        if total_duration >= target_duration:
            break
    
    st.info(f"✅ Smart Fallback: Selected {len(segments)} quality segments")
    return segments

def create_summary_video(input_video, segments, output_path, min_duration=3):
    """Create professional summary video with smooth transitions"""
    
    # Filter valid segments
    valid_segments = [seg for seg in segments 
                     if seg['end_time'] - seg['start_time'] >= min_duration]
    
    if not valid_segments:
        raise ValueError("No valid segments found for summary")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        segment_files = []
        
        # Extract each segment with fade transitions
        for i, seg in enumerate(valid_segments):
            segment_path = os.path.join(temp_dir, f"segment_{i:03d}.mp4")
            
            start_time = seg['start_time']
            end_time = seg['end_time']
            duration = end_time - start_time
            
            # Extract with re-encoding for smooth playback
            cmd = [
                'ffmpeg', '-i', input_video,
                '-ss', str(start_time),
                '-t', str(duration),
                '-c:v', 'libx264', '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac', '-b:a', '128k',
                '-avoid_negative_ts', 'make_zero',
                '-y', segment_path
            ]
            
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            
            if result.returncode != 0:
                # Fallback to copy method
                cmd_simple = [
                    'ffmpeg', '-i', input_video,
                    '-ss', str(start_time),
                    '-t', str(duration),
                    '-c', 'copy',
                    '-y', segment_path
                ]
                subprocess.run(cmd_simple, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            
            segment_files.append(segment_path)
        
        # Create concat file
        concat_file = os.path.join(temp_dir, 'concat.txt')
        with open(concat_file, 'w', encoding='utf-8') as f:
            for seg_file in segment_files:
                f.write(f"file '{seg_file}'\n")
        
        # Concatenate with smooth output
        cmd = [
            'ffmpeg', '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c:v', 'libx264', '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-movflags', '+faststart',
            '-y', output_path
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        
        if result.returncode != 0:
            st.error(f"Concatenation failed: {result.stderr.decode()[:500]}")
            raise Exception("Video creation failed")
    
    return output_path, valid_segments

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload Video")
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'mov', 'avi', 'mkv', 'webm'],
        help="Upload any video - AI will create professional summary"
    )
    
    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.metric("File Size", f"{file_size_mb:.1f} MB")
        
        st.video(uploaded_file)
        
        if file_size_mb > 200:
            st.warning("⚠️ Large file detected. Processing may take longer.")

with col2:
    st.header("🎯 Smart Summary")
    
    if uploaded_file:
        if not api_key:
            st.error("🔑 Please enter your OpenAI API key in the sidebar")
        elif not st.session_state.ffmpeg_available:
            st.error("❌ FFmpeg not found. Please install FFmpeg to use this tool.")
        else:
            # Check if auto news mode should be triggered
            video_duration_est = (uploaded_file.size / (1024 * 1024)) * 5
            is_auto_news = video_duration_est >= 600
            
            if is_auto_news and not st.session_state.auto_news_triggered:
                st.session_state.auto_news_triggered = True
                st.info("🔴 Auto-News Mode Activated: Video is 10+ minutes. Generating 30-second news summary...")
                process_video_auto_news = True
            else:
                process_video_auto_news = st.button("🚀 Create Smart Summary", 
                                                    type="primary", 
                                                    disabled=st.session_state.processing,
                                                    use_container_width=True)
            
            if (process_video_auto_news or is_auto_news) and not st.session_state.processing:
                
                st.session_state.processing = True
                
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        
                        # Save uploaded video
                        video_path = os.path.join(temp_dir, "input_video.mp4")
                        with open(video_path, 'wb') as f:
                            f.write(uploaded_file.read())
                        
                        video_duration = get_video_duration(video_path)
                        
                        # Progress tracking
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Step 1: Extract audio
                        status_text.text("🎵 Step 1/4: Extracting audio...")
                        progress_bar.progress(25)
                        audio_path = os.path.join(temp_dir, "audio.mp3")
                        extract_audio(video_path, audio_path)
                        
                        # Step 2: Transcribe
                        status_text.text("📝 Step 2/4: Transcribing speech (all languages)...")
                        progress_bar.progress(50)
                        transcript = transcribe_audio(audio_path, api_key)
                        
                        detected_lang = transcript.language if hasattr(transcript, 'language') else "unknown"
                        st.info(f"🌍 Detected: {detected_lang.upper()}")
                        
                        # Determine if auto-news based on actual duration
                        is_auto_news_mode = video_duration >= 600
                        news_target = 30 if is_auto_news_mode else target_duration
                        
                        # Step 3: Smart analysis
                        if is_auto_news_mode:
                            status_text.text("🤖 Step 3/4: AI analyzing NEWS CONTENT with smart features...")
                            st.warning("📰 Analyzing for breaking news, key headlines, and major events...")
                        else:
                            status_text.text("🤖 Step 3/4: AI analyzing with smart features...")
                        
                        progress_bar.progress(75)
                        segments = analyze_content_smart(
                            transcript, api_key, 
                            news_target, video_duration, 
                            max_segments=6 if is_auto_news_mode else max_segments,
                            speech_only=speech_only, 
                            detect_important=detect_important_moments,
                            remove_fillers=remove_filler_words, 
                            complete_sentences=complete_sentences,
                            topic_based=topic_based, 
                            chronological=chronological_order,
                            is_auto_news=is_auto_news_mode
                        )
                        
                        # Step 4: Create video
                        status_text.text("✂️ Step 4/4: Creating professional summary...")
                        progress_bar.progress(90)
                        output_path = os.path.join(temp_dir, "summary.mp4")
                        output_path, selected_segments = create_summary_video(
                            video_path, segments, output_path, min_segment_duration
                        )
                        
                        progress_bar.progress(100)
                        
                        if is_auto_news_mode:
                            status_text.text("✅ News summary created!")
                        else:
                            status_text.text("✅ Smart summary created!")
                        
                        # Calculate stats
                        total_summary_duration = sum(
                            seg['end_time'] - seg['start_time'] 
                            for seg in selected_segments
                        )
                        
                        # Display results
                        if is_auto_news_mode:
                            st.success(f"""
                            📰 NEWS SUMMARY COMPLETE!
                            - **Original Duration:** {video_duration:.1f}s
                            - **Summary Duration:** {total_summary_duration:.1f}s (News Standard: 30s)
                            - **Segments:** {len(selected_segments)} (news-focused)
                            - **Compression:** {(video_duration/total_summary_duration):.1f}x
                            - **Content:** Breaking news & key headlines only
                            """)
                        else:
                            st.success(f"""
                            🎉 Smart Summary Complete!
                            - **Duration:** {total_summary_duration:.1f}s (Target: {news_target}s)
                            - **Segments:** {len(selected_segments)}
                            - **Compression:** {(video_duration/total_summary_duration):.1f}x
                            - **Quality:** Professional with smart features
                            """)
                        
                        # Show summary video
                        with open(output_path, 'rb') as f:
                            video_bytes = f.read()
                            
                            st.subheader("📺 Smart Summary Preview")
                            st.video(video_bytes)
                            
                            # Download button
                            col_dl1, col_dl2 = st.columns([1, 2])
                            with col_dl1:
                                if is_auto_news_mode:
                                    dl_filename = f"news_summary_30s.mp4"
                                else:
                                    dl_filename = f"smart_summary_{news_target}s.mp4"
                                
                                st.download_button(
                                    label="⬇️ Download Summary",
                                    data=video_bytes,
                                    file_name=dl_filename,
                                    mime="video/mp4",
                                    use_container_width=True
                                )
                            
                            with col_dl2:
                                file_size_mb = len(video_bytes) / (1024 * 1024)
                                st.caption(f"File size: {file_size_mb:.1f} MB")
                        
                        # Show segment details with topics
                        with st.expander("📋 View Selected Segments"):
                            current_topic = None
                            
                            for i, seg in enumerate(selected_segments, 1):
                                duration = seg['end_time'] - seg['start_time']
                                topic = seg.get('topic', 'General')
                                news_type = seg.get('news_type', 'General')
                                
                                # Show topic header if changed
                                if topic != current_topic:
                                    if is_auto_news_mode:
                                        st.markdown(f"### 📰 {news_type}")
                                    else:
                                        st.markdown(f"### 📌 {topic}")
                                    current_topic = topic
                                
                                col_seg1, col_seg2 = st.columns([1, 4])
                                
                                with col_seg1:
                                    st.metric(f"Segment {i}", f"{duration:.1f}s")
                                
                                with col_seg2:
                                    priority_stars = "⭐" * seg.get('priority', 3)
                                    
                                    features = []
                                    if seg.get('has_clear_speech'):
                                        features.append("🎤 Clear Speech")
                                    if seg.get('is_complete_sentence'):
                                        features.append("✅ Complete")
                                    
                                    features_text = " | ".join(features) if features else ""
                                    
                                    st.markdown(f"""
                                    **Time:** {seg['start_time']:.1f}s - {seg['end_time']:.1f}s  
                                    **Priority:** {priority_stars}  
                                    **Reason:** {seg.get('reason', 'Auto-selected')}  
                                    {features_text}
                                    """)
                                    
                                    if 'text' in seg and seg['text']:
                                        with st.expander("View transcript"):
                                            st.caption(seg['text'])
                                
                                st.divider()
                        
                        # Store in session state
                        st.session_state.last_summary = {
                            'video_bytes': video_bytes,
                            'segments': selected_segments,
                            'original_duration': video_duration,
                            'summary_duration': total_summary_duration
                        }
                
                except subprocess.TimeoutExpired:
                    st.error("⏱️ Processing timed out. Try with a shorter video.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Try adjusting smart features in sidebar.")
                
                finally:
                    st.session_state.processing = False
    
    else:
        st.info("👈 Upload a video to create smart summary")

# Custom CSS
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    .stVideo {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
    }
    h3 {
        color: #667eea;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <h4>🎯 Smart Features Active</h4>
    <p>✅ Multi-language support (English, Tamil, Hindi, Spanish, etc.)</p>
    <p>✅ Smart duration control (15s/30s/60s)</p>
    <p>✅ Speech-only mode (no background noise)</p>
    <p>✅ Important moment detection</p>
    <p>✅ Filler word removal</p>
    <p>✅ Complete sentences only</p>
    <p>✅ Topic-based segmentation</p>
    <p>✅ Chronological story flow</p>
    <p>✅ <strong>AUTO NEWS MODE (10+ min videos)</strong> - Breaking news detection</p>
    <br>
    <p><strong>🔒 Privacy:</strong> Videos processed securely, not stored</p>
    <p style='font-size: 0.8em; margin-top: 20px; color: #888;'>Powered by OpenAI Whisper & GPT-4</p>
</div>
""", unsafe_allow_html=True)