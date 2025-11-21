# Imagen base oficial de Python + Debian estable
FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Dependencias necesarias para Playwright Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl unzip git \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdbus-1-3 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libasound2 \
    libpangocairo-1.0-0 libpango-1.0-0 libcairo2 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements
COPY requirements.txt /app/requirements.txt

# Instalar dependencias Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Instalar Playwright y navegador
RUN pip install playwright
RUN playwright install chromium

# Copiar código del proyecto
COPY . /app/

# Railway usa este puerto
EXPOSE 8080

# NUNCA usar Gunicorn sync (rompe Playwright async)
# Usamos worker uvicorn (ASGI/async compatible)
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker wsgi:app --bind 0.0.0.0:${PORT}"]

