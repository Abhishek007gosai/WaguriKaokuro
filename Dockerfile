FROM python:3.10-slim

WORKDIR /app

# System deps: gcc/libffi for TgCrypto, ffmpeg for media rename/convert
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Koyeb / Render inject PORT; default 8080 for local runs
ENV PORT=8080
EXPOSE 8080

# Prefer bot.py (real entrypoint). main.py is only a fallback for platforms
# that default to python main.py.
CMD ["python", "bot.py"]
