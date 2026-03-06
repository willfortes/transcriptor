# Deploy no Coolify

## Configuração

- **Build**: Dockerfile na raiz do repositório (build padrão).
- **Porta**: `8501` (Streamlit).
- **Comando**: não é necessário sobrescrever; o `CMD` do Dockerfile já inicia o Streamlit.

## Passos no Coolify

1. **Novo recurso** → Application → **Git Repository** (ou Docker Compose, se preferir).
2. **Repositório**: URL do seu repositório (ex.: `https://github.com/seu-usuario/trans-midia`).
3. **Build**:
   - **Dockerfile path**: `Dockerfile` (raiz).
   - **Context**: `.` (raiz).
4. **Ports**: mapear porta do container `8501` para a porta pública desejada (ex. 8501 ou 80).
5. **Deploy**: o primeiro build pode demorar alguns minutos (download do PyTorch CPU e do modelo Whisper).

## Variáveis de ambiente (opcional)

| Variável | Descrição |
|----------|-----------|
| `STREAMLIT_SERVER_PORT` | Porta do Streamlit (padrão: 8501). |

## Observações

- A imagem usa **PyTorch CPU-only** para build mais rápido e estável (sem GPU).
- O modelo Whisper usado é o **base**; o download ocorre na primeira transcrição.
- Para mais memória/CPU no primeiro uso, ajuste os recursos do serviço no Coolify.
