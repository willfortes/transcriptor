# Trans-Midia - Transcrição de vídeo/áudio com Whisper
# Otimizado para deploy no Coolify (torch CPU-only para build estável)

FROM python:3.10-slim-bookworm

# Dependências de sistema (ffmpeg para yt-dlp e processamento de áudio)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar PyTorch CPU-only primeiro (evita imagem gigante e timeout no build)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Dependências Python (torch já instalado acima)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código da aplicação
COPY . .

# Usuário não-root para segurança
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

# Streamlit: porta e bind em 0.0.0.0 para acesso externo
ENV STREAMLIT_SERVER_PORT=8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
