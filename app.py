import os
import tempfile
import streamlit as st
import whisper
import yt_dlp
from st_copy_to_clipboard import st_copy_to_clipboard

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Video/Audio Transcriber", layout="centered")

st.title("🎙️ Video & Audio Transcriber")
st.write("Upload a file or download from YouTube and transcribe automatically.")

# -----------------------------
# LOAD MODEL
# -----------------------------
@st.cache_resource
def load_model():
    return whisper.load_model("base")  # tiny, base, small, medium, large

model = load_model()

# -----------------------------
# YOUTUBE DOWNLOAD FUNCTION
# -----------------------------
def download_youtube_audio(url, output_path):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# -----------------------------
# TRANSCRIBE FUNCTION
# -----------------------------
def transcribe(file_path):
    result = model.transcribe(file_path)
    return result["text"]

# -----------------------------
# STORE TRANSCRIPTION
# -----------------------------
if "transcription_text" not in st.session_state:
    st.session_state.transcription_text = ""

# -----------------------------
# UI TABS
# -----------------------------
tab1, tab2 = st.tabs(["📥 Upload File", "📺 YouTube URL"])

# -----------------------------
# TAB 1 - UPLOAD
# -----------------------------
with tab1:
    uploaded_file = st.file_uploader(
        "Upload video or audio",
        type=["mp4", "mov", "avi", "mkv", "mp3", "wav", "ogg"]
    )

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name

        if st.button("Transcribe Upload"):
            with st.spinner("Transcribing..."):
                text = transcribe(temp_path)
                st.session_state.transcription_text = text
                st.success("Transcription complete!")

        os.unlink(temp_path)

# -----------------------------
# TAB 2 - YOUTUBE
# -----------------------------
with tab2:
    youtube_url = st.text_input("Paste YouTube URL")

    if st.button("Download & Transcribe"):
        if youtube_url:
            with tempfile.TemporaryDirectory() as tmp_dir:
                output_template = os.path.join(tmp_dir, "%(title)s.%(ext)s")

                with st.spinner("Downloading audio..."):
                    download_youtube_audio(youtube_url, output_template)

                files = os.listdir(tmp_dir)
                audio_path = os.path.join(tmp_dir, files[0])

                with st.spinner("Transcribing..."):
                    text = transcribe(audio_path)
                    st.session_state.transcription_text = text

                st.success("Transcription complete!")

# -----------------------------
# TRANSCRIPTION OUTPUT AREA
# -----------------------------
if st.session_state.transcription_text:

    st.text_area(
        "Transcription",
        st.session_state.transcription_text,
        height=300
    )

    col1, col2, col3 = st.columns(3)

    # Copy Button (JS hack)
    with col1:
        st_copy_to_clipboard(
            st.session_state.transcription_text,
            "📋 Copy Text"
        )

    # Export TXT
    with col2:
        st.download_button(
            label="⬇️ Export TXT",
            data=st.session_state.transcription_text,
            file_name="transcription.txt",
            mime="text/plain"
        )

    # Export MD
    with col3:
        markdown_content = f"# Transcription\n\n{st.session_state.transcription_text}"

        st.download_button(
            label="⬇️ Export MD",
            data=markdown_content,
            file_name="transcription.md",
            mime="text/markdown"
        )