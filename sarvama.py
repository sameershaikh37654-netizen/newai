# import re
# import os
# import base64
# import streamlit as st
# from pydub import AudioSegment
# from sarvamai import SarvamAI

# # Page configuration
# st.set_page_config(
#     page_title="Telugu Text-to-Speech",
#     page_icon="🎙️",
#     layout="wide"
# )

# # Title and description
# st.title("🎙️ Telugu Text-to-Speech Generator")
# st.markdown("Convert Telugu text to speech using Sarvam AI")

# # All available Sarvam AI voices with descriptions
# VOICE_PRESETS = {
#     "anushka": {"name": "Anushka", "gender": "Female", "style": "Clear & Professional"},
#     "vidya": {"name": "Vidya", "gender": "Female", "style": "General Purpose"},
#     "manisha": {"name": "Manisha", "gender": "Female", "style": "Educational"},
#     "arya": {"name": "Arya", "gender": "Female", "style": "News & Announcements"},
#     "meera": {"name": "Meera", "gender": "Female", "style": "Conversational"},
#     "kavya": {"name": "Kavya", "gender": "Female", "style": "Storytelling"},
#     "abhilash": {"name": "Abhilash", "gender": "Male", "style": "Authoritative"},
#     "karun": {"name": "Karun", "gender": "Male", "style": "Conversational"},
#     "hitesh": {"name": "Hitesh", "gender": "Male", "style": "General Purpose"}
# }

# # Sidebar for API key and settings
# with st.sidebar:
#     st.header("⚙️ Settings")
#     api_key = st.text_input(
#         "API Key",
#         value="sk_4ahlbb9f_eqTiZbLVHWE5m22dbplG4eys",
#         type="password",
#         help="Enter your Sarvam AI API key"
#     )
    
#     sample_rate = st.selectbox(
#         "Sample Rate",
#         [8000, 16000, 22050, 44100],
#         index=2,
#         help="Audio quality (higher = better quality but larger file)"
#     )

# # Voice Selection Section
# st.subheader("🎤 Select Anchor Voice")
# st.markdown("Choose your preferred voice from the options below:")

# # Method 1: Radio buttons for voice selection
# voice_options = list(VOICE_PRESETS.keys())
# speaker = st.radio(
#     "Choose Anchor Voice:",
#     options=voice_options,
#     format_func=lambda x: f"{VOICE_PRESETS[x]['name']} ({VOICE_PRESETS[x]['gender']}) - {VOICE_PRESETS[x]['style']}",
#     horizontal=False,
#     help="Select your preferred anchor voice"
# )

# # Display selected voice info
# col1, col2, col3 = st.columns(3)
# with col1:
#     st.info(f"**Selected:** {VOICE_PRESETS[speaker]['name']}")
# with col2:
#     st.info(f"**Gender:** {VOICE_PRESETS[speaker]['gender']}")
# with col3:
#     st.info(f"**Style:** {VOICE_PRESETS[speaker]['style']}")

# # Alternative: Buttons for quick voice switching (uncomment to use)
# st.markdown("---")
# st.subheader("🔀 Quick Voice Switch")
# st.markdown("Click any button below to instantly change the anchor voice:")

# # Create buttons for each voice
# button_cols = st.columns(3)
# button_index = 0
# for voice_id, voice_info in VOICE_PRESETS.items():
#     with button_cols[button_index % 3]:
#         if st.button(f"🎙️ {voice_info['name']}", key=f"btn_{voice_id}", use_container_width=True):
#             speaker = voice_id
#             st.success(f"✓ Voice changed to {voice_info['name']}")
#             st.rerun()  # Refresh to show updated selection
#     button_index += 1

# # Default Telugu news text
# default_text = """తెలుగు రోడ్ సేఫ్టీ ముఖ్య వార్తా కథనం ఈ దేశంలో రహదారి ప్రమాదాలు ఇంకా ఒక అత్యవసర సమస్యగా కొనసాగుతున్నాయి. ఇటీవల విడుదలైన కేంద్ర సర్కార్ గణాంకాల ప్రకారం, గత ఐదు సంవత్సరాల్లో దేశవ్యాప్తంగా రోడ్డు ప్రమాదాల్లో సుమారు 7.77 లక్షల మంది ప్రాణాలు కోల్పోయారు మరియు వేలాది మంది గాయపడ్డారు, ఇది రహదారి భద్రతపై తీవ్ర ఆందోళనను చూపుతుందని ప్రతిపాదించబడింది."""

# # Text input area
# st.subheader("📝 Enter Telugu Text")
# input_text = st.text_area(
#     "Text to convert",
#     value=default_text,
#     height=200,
#     help="Enter or paste Telugu text here"
# )

# # Character count
# st.caption(f"Characters: {len(input_text)}")

# # Voice characteristics controls
# st.subheader("🎚️ Voice Controls (Advanced)")
# col1, col2, col3 = st.columns(3)
# with col1:
#     pitch = st.slider("Pitch", -1.0, 1.0, 0.0, 0.1, 
#                       help="Adjust voice pitch (-1 to 1)")
# with col2:
#     pace = st.slider("Pace", 0.3, 3.0, 1.0, 0.1,
#                      help="Adjust speech speed (0.3 to 3)")
# with col3:
#     loudness = st.slider("Loudness", 0.1, 3.0, 1.0, 0.1,
#                          help="Adjust volume (0.1 to 3)")

# # Generate button
# st.markdown("---")
# col1, col2, col3 = st.columns([1, 2, 1])
# with col2:
#     generate_button = st.button(
#         f"🎵 Generate Speech with {VOICE_PRESETS[speaker]['name']}", 
#         use_container_width=True, 
#         type="primary"
#     )

# # Processing and generation
# if generate_button:
#     if not input_text.strip():
#         st.error("⚠️ Please enter some Telugu text!")
#     elif not api_key:
#         st.error("⚠️ Please enter your API key in the sidebar!")
#     else:
#         try:
#             # Initialize client
#             client = SarvamAI(api_subscription_key=api_key)
            
#             # Progress tracking
#             progress_bar = st.progress(0)
#             status_text = st.empty()
            
#             # Display selected parameters
#             voice_info = VOICE_PRESETS[speaker]
#             st.info(f"**Voice:** {voice_info['name']} | **Sample Rate:** {sample_rate}Hz | **Language:** Telugu (te-IN)")
            
#             # Split into chunks
#             status_text.text("📋 Splitting text into chunks...")
#             raw_chunks = re.split(r'(?<=[।\.\?\!])\s+', input_text.strip())
#             valid_chunks = [
#                 chunk for chunk in raw_chunks
#                 if len(chunk.strip()) > 3 and re.search(r'[\u0C00-\u0C7F]', chunk)
#             ]
            
#             st.info(f"✅ Found {len(valid_chunks)} valid text chunks")
            
#             # Create temporary directory
#             os.makedirs("tmp_mp3s", exist_ok=True)
#             chunk_files = []
            
#             # Generate audio for each chunk
#             for i, sentence in enumerate(valid_chunks):
#                 progress = (i + 1) / len(valid_chunks)
#                 progress_bar.progress(progress)
#                 status_text.text(f"🎤 Generating audio chunk {i+1}/{len(valid_chunks)}...")
                
#                 response = client.text_to_speech.convert(
#                     text=sentence,
#                     target_language_code="te-IN",
#                     speaker=speaker,
#                     pitch=pitch,
#                     pace=pace,
#                     loudness=loudness,
#                     output_audio_codec="mp3",
#                     speech_sample_rate=sample_rate,
#                     enable_preprocessing=True,
#                     model="bulbul:v2"
#                 )
                
#                 chunk_name = f"tmp_mp3s/chunk_{i}.mp3"
#                 with open(chunk_name, "wb") as f:
#                     for audio_base64 in response.audios:
#                         f.write(base64.b64decode(audio_base64))
                
#                 chunk_files.append(chunk_name)
            
#             # Combine audio chunks
#             status_text.text("🔗 Combining audio chunks...")
#             combined = AudioSegment.empty()
#             for chunk in chunk_files:
#                 combined += AudioSegment.from_mp3(chunk)
            
#             # Export final file
#             final_file = f"telugu_speech_{speaker}_{sample_rate}hz.mp3"
#             combined.export(final_file, format="mp3")
            
#             # Clear progress indicators
#             progress_bar.empty()
#             status_text.empty()
            
#             # Success message and audio player
#             st.success(f"✅ Audio generated successfully with {voice_info['name']} voice!")
            
#             # Display audio player
#             st.subheader("🔊 Generated Audio")
#             with open(final_file, "rb") as audio_file:
#                 audio_bytes = audio_file.read()
#                 st.audio(audio_bytes, format="audio/mp3")
            
#             # Download button
#             st.download_button(
#                 label=f"⬇️ Download MP3 ({voice_info['name']})",
#                 data=audio_bytes,
#                 file_name=final_file,
#                 mime="audio/mp3",
#                 use_container_width=True
#             )
            
#             # Cleanup option
#             with st.expander("🗑️ Cleanup Options"):
#                 if st.button("Delete temporary files"):
#                     for chunk in chunk_files:
#                         if os.path.exists(chunk):
#                             os.remove(chunk)
#                     if os.path.exists("tmp_mp3s") and not os.listdir("tmp_mp3s"):
#                         os.rmdir("tmp_mp3s")
#                     st.success("Temporary files cleaned up!")
                
#         except Exception as e:
#             st.error(f"❌ Error: {str(e)}")
#             st.exception(e)

# # Footer
# st.markdown("---")
# st.markdown(
#     """
#     <div style='text-align: center; color: gray;'>
#         Built with Streamlit & Sarvam AI | Uses Bulbul-V2 TTS Model | Supports 9 Anchor Voices
#     </div>
#     """,
#     unsafe_allow_html=True
# )
















import re
import os
import base64
import glob
import streamlit as st
from pydub import AudioSegment
from sarvamai import SarvamAI

# Page configuration
st.set_page_config(
    page_title="Telugu Text-to-Speech",
    page_icon="🎙️",
    layout="wide"
)

# Output folder configuration
OUTPUT_FOLDER = r"C:\Users\GLOBAL T\Desktop\output"

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_next_filename():
    """Get the next sequential filename (tts_1, tts_2, etc.)"""
    existing_files = glob.glob(os.path.join(OUTPUT_FOLDER, "tts_*.mp3"))
    if not existing_files:
        return "tts_1.mp3"
    
    # Extract numbers from existing filenames
    numbers = []
    for f in existing_files:
        basename = os.path.basename(f)
        match = re.search(r'tts_(\d+)\.mp3', basename)
        if match:
            numbers.append(int(match.group(1)))
    
    next_num = max(numbers) + 1 if numbers else 1
    return f"tts_{next_num}.mp3"

# Title and description
st.title("🎙️ Telugu Text-to-Speech Generator")
st.markdown("Convert Telugu text to speech using Sarvam AI")
st.info(f"📁 Output folder: `{OUTPUT_FOLDER}`")

# All available Sarvam AI voices with descriptions
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

# Initialize session state for speaker
if 'speaker' not in st.session_state:
    st.session_state.speaker = "anushka"

# Sidebar for API key and settings
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "API Key",
        value="sk_4ahlbb9f_eqTiZbLVHWE5m22dbplG4eys",
        type="password",
        help="Enter your Sarvam AI API key"
    )
    
    sample_rate = st.selectbox(
        "Sample Rate",
        [8000, 16000, 22050, 44100],
        index=2,
        help="Audio quality (higher = better quality but larger file)"
    )
    
    st.markdown("---")
    st.subheader("📂 Output Info")
    st.write(f"**Folder:** {OUTPUT_FOLDER}")
    
    # Show existing files count
    existing_files = glob.glob(os.path.join(OUTPUT_FOLDER, "tts_*.mp3"))
    st.write(f"**Files generated:** {len(existing_files)}")
    
    # Show next filename
    next_file = get_next_filename()
    st.write(f"**Next file:** {next_file}")

# Voice Selection Section
st.subheader("🎤 Select Anchor Voice")
st.markdown("Choose your preferred voice from the options below:")

# Radio buttons for voice selection
voice_options = list(VOICE_PRESETS.keys())
speaker = st.radio(
    "Choose Anchor Voice:",
    options=voice_options,
    format_func=lambda x: f"{VOICE_PRESETS[x]['name']} ({VOICE_PRESETS[x]['gender']}) - {VOICE_PRESETS[x]['style']}",
    horizontal=False,
    help="Select your preferred anchor voice",
    index=voice_options.index(st.session_state.speaker)
)

# Update session state
st.session_state.speaker = speaker

# Display selected voice info
col1, col2, col3 = st.columns(3)
with col1:
    st.info(f"**Selected:** {VOICE_PRESETS[speaker]['name']}")
with col2:
    st.info(f"**Gender:** {VOICE_PRESETS[speaker]['gender']}")
with col3:
    st.info(f"**Style:** {VOICE_PRESETS[speaker]['style']}")

# Quick Voice Switch buttons
st.markdown("---")
st.subheader("🔀 Quick Voice Switch")
st.markdown("Click any button below to instantly change the anchor voice:")

# Create buttons for each voice
button_cols = st.columns(3)
button_index = 0
for voice_id, voice_info in VOICE_PRESETS.items():
    with button_cols[button_index % 3]:
        if st.button(f"🎙️ {voice_info['name']}", key=f"btn_{voice_id}", use_container_width=True):
            st.session_state.speaker = voice_id
            st.success(f"✓ Voice changed to {voice_info['name']}")
            st.rerun()
    button_index += 1

# Use session state speaker
speaker = st.session_state.speaker

# Default Telugu news text
default_text = """తెలుగు రోడ్ సేఫ్టీ ముఖ్య వార్తా కథనం ఈ దేశంలో రహదారి ప్రమాదాలు ఇంకా ఒక అత్యవసర సమస్యగా కొనసాగుతున్నాయి. ఇటీవల విడుదలైన కేంద్ర సర్కార్ గణాంకాల ప్రకారం, గత ఐదు సంవత్సరాల్లో దేశవ్యాప్తంగా రోడ్డు ప్రమాదాల్లో సుమారు 7.77 లక్షల మంది ప్రాణాలు కోల్పోయారు మరియు వేలాది మంది గాయపడ్డారు, ఇది రహదారి భద్రతపై తీవ్ర ఆందోళనను చూపుతుందని ప్రతిపాదించబడింది."""

# Text input area
st.subheader("📝 Enter Telugu Text")
input_text = st.text_area(
    "Text to convert",
    value=default_text,
    height=200,
    help="Enter or paste Telugu text here"
)

# Character count
st.caption(f"Characters: {len(input_text)}")

# Voice characteristics controls
st.subheader("🎚️ Voice Controls (Advanced)")
col1, col2, col3 = st.columns(3)
with col1:
    pitch = st.slider("Pitch", -1.0, 1.0, 0.0, 0.1, 
                      help="Adjust voice pitch (-1 to 1)")
with col2:
    pace = st.slider("Pace", 0.3, 3.0, 1.0, 0.1,
                     help="Adjust speech speed (0.3 to 3)")
with col3:
    loudness = st.slider("Loudness", 0.1, 3.0, 1.0, 0.1,
                         help="Adjust volume (0.1 to 3)")

# Generate button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button(
        f"🎵 Generate Speech with {VOICE_PRESETS[speaker]['name']}", 
        use_container_width=True, 
        type="primary"
    )

# Processing and generation
if generate_button:
    if not input_text.strip():
        st.error("⚠️ Please enter some Telugu text!")
    elif not api_key:
        st.error("⚠️ Please enter your API key in the sidebar!")
    else:
        try:
            # Initialize client
            client = SarvamAI(api_subscription_key=api_key)
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Display selected parameters
            voice_info = VOICE_PRESETS[speaker]
            st.info(f"**Voice:** {voice_info['name']} | **Sample Rate:** {sample_rate}Hz | **Language:** Telugu (te-IN)")
            
            # Split into chunks
            status_text.text("📋 Splitting text into chunks...")
            raw_chunks = re.split(r'(?<=[।\.\?\!])\s+', input_text.strip())
            valid_chunks = [
                chunk for chunk in raw_chunks
                if len(chunk.strip()) > 3 and re.search(r'[\u0C00-\u0C7F]', chunk)
            ]
            
            st.info(f"✅ Found {len(valid_chunks)} valid text chunks")
            
            # Create temporary directory for chunks
            temp_folder = os.path.join(OUTPUT_FOLDER, "tmp_chunks")
            os.makedirs(temp_folder, exist_ok=True)
            chunk_files = []
            
            # Generate audio for each chunk
            for i, sentence in enumerate(valid_chunks):
                progress = (i + 1) / len(valid_chunks)
                progress_bar.progress(progress)
                status_text.text(f"🎤 Generating audio chunk {i+1}/{len(valid_chunks)}...")
                
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
                
                chunk_name = os.path.join(temp_folder, f"chunk_{i}.mp3")
                with open(chunk_name, "wb") as f:
                    for audio_base64 in response.audios:
                        f.write(base64.b64decode(audio_base64))
                
                chunk_files.append(chunk_name)
            
            # Combine audio chunks
            status_text.text("🔗 Combining audio chunks...")
            combined = AudioSegment.empty()
            for chunk in chunk_files:
                combined += AudioSegment.from_mp3(chunk)
            
            # Get sequential filename and save to output folder
            output_filename = get_next_filename()
            final_file = os.path.join(OUTPUT_FOLDER, output_filename)
            combined.export(final_file, format="mp3")
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Success message and audio player
            st.success(f"✅ Audio generated successfully!")
            st.success(f"📁 Saved as: `{final_file}`")
            
            # Display audio player
            st.subheader("🔊 Generated Audio")
            with open(final_file, "rb") as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mp3")
            
            # Download button
            st.download_button(
                label=f"⬇️ Download MP3 ({output_filename})",
                data=audio_bytes,
                file_name=output_filename,
                mime="audio/mp3",
                use_container_width=True
            )
            
            # Cleanup temporary chunk files
            status_text.text("🗑️ Cleaning up temporary files...")
            for chunk in chunk_files:
                if os.path.exists(chunk):
                    os.remove(chunk)
            if os.path.exists(temp_folder) and not os.listdir(temp_folder):
                os.rmdir(temp_folder)
            status_text.empty()
            
            # Show all generated files
            with st.expander("📂 View All Generated Files"):
                all_files = sorted(glob.glob(os.path.join(OUTPUT_FOLDER, "tts_*.mp3")))
                if all_files:
                    for f in all_files:
                        st.write(f"• {os.path.basename(f)}")
                else:
                    st.write("No files generated yet.")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

# Show existing outputs section
st.markdown("---")
st.subheader("📂 Generated Files")
existing_files = sorted(glob.glob(os.path.join(OUTPUT_FOLDER, "tts_*.mp3")))
if existing_files:
    st.write(f"**Total files:** {len(existing_files)}")
    
    # Display files in expandable section
    with st.expander("View/Play Generated Files"):
        for file_path in existing_files[-5:]:  # Show last 5 files
            filename = os.path.basename(file_path)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"🎵 {filename}")
            with col2:
                with open(file_path, "rb") as f:
                    st.download_button(
                        "⬇️",
                        data=f.read(),
                        file_name=filename,
                        mime="audio/mp3",
                        key=f"dl_{filename}"
                    )
        if len(existing_files) > 5:
            st.caption(f"...and {len(existing_files) - 5} more files")
else:
    st.info("No files generated yet. Generate your first audio above!")

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray;'>
        Built with Streamlit & Sarvam AI | Uses Bulbul-V2 TTS Model | Supports 9 Anchor Voices<br>
        Output folder: {OUTPUT_FOLDER}
    </div>
    """,
    unsafe_allow_html=True
)