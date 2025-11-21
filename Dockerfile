# Imagen base oficial
FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Dependencias básicas para Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl unzip git \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdbus-1-3 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libasound2 \
    libpangocairo-1.0-0 libpango-1.0-0 libcairo2 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Instalar playwright + chromium
RUN pip install playwright
RUN playwright install chromium

# Copiar proyecto
COPY . /app/

# Railway expone este puerto
EXPOSE 8080

# Ejecutar Flask con Gunicorn (WSGI)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]
