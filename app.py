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
def download_youtube_audio(url, output_path, cookiefile=None):
    ydl_opts = {
        # "best" aceita qualquer formato disponível; FFmpegExtractAudio extrai o áudio para mp3
        "format": "best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        # Reduz bloqueio "Sign in to confirm you're not a bot" (IPs de datacenter)
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        "quiet": True,
    }
    if cookiefile and os.path.isfile(cookiefile):
        ydl_opts["cookiefile"] = cookiefile

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
    youtube_url = st.text_input("Cole a URL do YouTube")

    with st.expander("Se o YouTube pedir login (anti-bot): usar cookies"):
        st.caption("Exporte os cookies do YouTube no seu navegador (extensão ou yt-dlp) e envie aqui.")
        cookies_file_upload = st.file_uploader("Arquivo cookies.txt (opcional)", type=["txt"], key="yt_cookies")

    if st.button("Download & Transcribe"):
        if youtube_url:
            cookiefile = os.environ.get("YT_COOKIES_FILE")
            cookie_temp_path = None
            if cookies_file_upload:
                with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".txt") as cf:
                    cf.write(cookies_file_upload.read())
                    cookie_temp_path = cf.name
                    cookiefile = cookie_temp_path

            try:
                with tempfile.TemporaryDirectory() as tmp_dir:
                    output_template = os.path.join(tmp_dir, "%(title)s.%(ext)s")

                    with st.spinner("Baixando áudio..."):
                        download_youtube_audio(youtube_url, output_template, cookiefile=cookiefile)

                    files = [f for f in os.listdir(tmp_dir) if not f.endswith(".part")]
                    if not files:
                        st.error("Nenhum áudio baixado. Tente usar cookies (expandir acima) ou outro vídeo.")
                    else:
                        audio_path = os.path.join(tmp_dir, files[0])

                        with st.spinner("Transcrevendo..."):
                            text = transcribe(audio_path)
                            st.session_state.transcription_text = text

                        st.success("Transcrição concluída!")
            except Exception as e:
                err = str(e)
                if "Sign in" in err or "bot" in err.lower() or "cookies" in err.lower():
                    st.error("YouTube bloqueou o acesso. Use a opção de cookies acima (exporte do seu navegador).")
                else:
                    st.error(f"Erro: {err}")
            finally:
                if cookie_temp_path and os.path.isfile(cookie_temp_path):
                    try:
                        os.unlink(cookie_temp_path)
                    except Exception:
                        pass

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