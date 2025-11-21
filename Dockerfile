# Imagen base
FROM python:3.10-bullseye

# Desactivar prompts
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Dependencias de Chromium (Playwright)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    git \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libxshmfence1 \
    libglib2.0-0 \
    libx11-xcb1 \
    libxtst6 \
    libxinerama1 \
    libgtk-3-0 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements
COPY requirements.txt /app/requirements.txt

# Instalar python deps
RUN pip install --upgrade pip && pip install -r requirements.txt

# Instalar Playwright + navegador Chromium
RUN pip install playwright && playwright install chromium

# Copiar proyecto completo
COPY . /app/

# Crear carpetas necesarias
RUN mkdir -p uploads salidas

# Puerto Railway
EXPOSE 8080

# Iniciar Flask
CMD ["python", "app.py"]
