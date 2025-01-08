# Usar a imagem mais leve de Python na versão 3.12
FROM python:3.12-slim

# Configurar variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1 \ 
    PYTHONUNBUFFERED=1

# Atualizar pacotes do sistema e instalar dependências necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Clonar o repositório do GitHub
# Utilizando autenticação com token armazenado como ARG
ARG GITHUB_TOKEN
RUN git clone https://$GITHUB_TOKEN@github.com/jmiguelh/mondayapi.git /app

# Instalar o Poetry
RUN pip install --no-cache-dir poetry

# Instalar dependências do projeto usando o Poetry
RUN poetry install --no-root

# Criar volume externo para a pasta /app/data
#VOLUME ["/app/data"]

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando padrão para executar o aplicativo
ENTRYPOINT ["streamlit", "run", "/app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
