FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y \
    espeak-ng-data \
    libespeak-ng1 \
    sox \
    libsndfile1 \
    libx11-6 \
    libx11-xcb1 \
    libpulse0 \
    libpcaudio0 \
    libcurl4 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/piper

# 🔥 Adiciona o caminho das bibliotecas para o executável encontrar
ENV LD_LIBRARY_PATH=/app

CMD ["python", "app.py"]

